from projects.models import Project, ProjectStats
import logging
import os
from datetime import datetime
import math
from django.conf import settings
import json
import pandas as pd

from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

GB = 1024 * 1024 * 1024
today = datetime.now()

def _monthly_stats(project, start_year, end_year):
    stats={}
    for year in range(start_year, end_year + 1):
        if year not in stats:
            stats[year] = {}
        for month in range(1, 13):
            if month not in stats[year]:
                stats[year][month] = {}
            s = ProjectStats.objects.filter(project=project, collected__year=year,
                                        collected__month=month).order_by('collected').last()
            if s is not None:
                stats[year][month]['size'] = float(s.size)
    return stats

def _yearly_stats(project, start_year, end_year):
    stats={}
    for year in range(start_year, end_year + 1):
        if year not in stats:
            stats[year] = {}
        s = ProjectStats.objects.filter(project=project, collected__year=year).order_by('collected').last()
        if s is not None:
            stats[year]['size'] = float(s.size)
    return stats



def get_usage_data(start_year, end_year, include_revisions=True):
    '''get monthly usage data for all projects from the databse

    Arguments:
        start_year {int} -- _description_
        end_year {int} -- _description_

    Returns:
        usage_data {dict} -- dict with project id as key and a dict with the project details and usage data as value
    '''    
    projects = Project.objects.filter(delete_date__isnull=True).all()
    usage_data = {}
    for project in projects:
        print(f'{project.name}')
        active = _monthly_stats(project, start_year, end_year)
        active_yearly = _yearly_stats(project, start_year, end_year)
        usage_data[project.id] = {
            'project': project.name,
            'usage_details': f'https://adminyoda.labs.vu.nl/projects/{project.id}',
            'created': project.create_date.strftime("%Y-%m-%d"),
            'deleted': project.delete_date.strftime("%Y-%m-%d") if project.delete_date else '',
            'owner_name': project.owner_name.name,
            'owner_vunetid': project.owner_name.username,
            'owner_email': project.owner_name.email,
            'budget_code': project.budget.code,
            'budget_type': project.budget.type,
            'budget_holder': project.budget.vunetid,
            'active': active, 
            'active_yearly': active_yearly,
        }
    return usage_data

def calculate_blocks(gigabytes, block_size_GB=1024):
    '''given a size in bytes, calculate the number of blocks of a given size in GB

    Arguments:
        bytes -- storage size in bytes

    Keyword Arguments:
        block_size_GB -- size of a block in GB (default: {1024})

    Returns:
        number of blocks {int} -- number of blocks of size block_size_GB
    '''    
    gigabytes = gigabytes + 0.0001 # avoid 0
    return int(math.ceil(gigabytes/block_size_GB))

def calculate_yearly_cost(size, free_block = 500, first_block = 2048, first_block_cost = 200, block_size = 1024, block_cost = 250):
    '''calculate yearly storage cost according to the VU pricing model.
    The default values are based on the costs for active storage. https://vu.nl/en/employee/research-data-support/costs-research-en-archiving-storage

    Arguments:
        size -- data size in bytes

    Keyword Arguments:
        free_block -- storage up to this size in GB is free (default: {500})
        first_block -- the first block over the free block has a specific price (default: {2048})
        first_block_cost -- cost of the first block (default: {200})
        block_size -- size of blocks for all storage over the first block (default: {1024})
        block_cost -- cost per block over first block (default: {250})

    Returns:
        calcluated cost per year in euros
    '''    
    total_cost = 0
    if size > free_block:
        total_cost = first_block_cost
    if size > first_block:
        total_cost = total_cost + (calculate_blocks(size - (first_block), block_size)) * block_cost
    return total_cost

def add_monthly_costs_to_projectdata(year, data):
    '''Loop through the data dict and use the monthly size to calculate the monthly costs

    Arguments:
        year {int} -- _description_
        data {dict} -- dict created by get_usage_data

    Returns:
        the data dict with the monthly costs added
    '''    
    for project in data:
        active_cost = 0
        if year in data[project]['active']:
            for month in data[project]['active'][year]:
                cost = 0
                if 'size' in data[project]['active'][year][month]:
                    cost = calculate_yearly_cost(data[project]['active'][year][month]['size']) / 12    
                    data[project]['active'][year][month]['cost'] = cost
                    active_cost += cost
            if 'size' in data[project]['active_yearly'][year]:
                data[project]['calculated_by_last'] = calculate_yearly_cost(data[project]['active_yearly'][year]['size'])
        data[project]['active_cost'] = active_cost
        data[project]['total_cost'] = active_cost
    return data

def get_billable_data(year, usage):
    '''add costs to the usage data, drop all free projects 

    Arguments:
        year {int} -- year to report
        usage {dict} -- usage data returned by get_usage_data

    Returns:
        bill_data {dict} -- usage data with added cost data, only projects with total cost>0
    '''    
    data=add_monthly_costs_to_projectdata(year, usage)
    bill_data = {}
    for project in data:
        if data[project]['total_cost'] > 0:
            bill_data[project] = data[project]
    return bill_data

def yearly_usage_formatted(year, data):
    '''usage data per month for each project in the billing data in useful format for pandas excel writer

    Arguments:
        year {integer} -- year to report
        data {dict} -- usage data created by get_usage_data

    Returns:
        report_usage_data {dict} -- usage data per month for each project in the billing data in useful format for pandas excel writer
    '''
    
    report_usage_data = {}
    row = 0
    for project in data:
        report_usage_data[row] = {}
        report_usage_data[row + 1] = {}
        report_usage_data[row + 2] = {}
        report_usage_data[row + 3] = {}
        report_usage_data[row]['project']=f'{data[project]["project"]}: size'
        report_usage_data[row + 1]['project']=f'{data[project]["project"]}: active_cost'
        for month in data[project]['active'][year]:
            if 'size' in data[project]['active'][year][month]:
                report_usage_data[row][month] = round(data[project]['active'][year][month]['size'])
                report_usage_data[row + 1][month] = round(data[project]['active'][year][month]['cost'], 2)
        row += 2
    return report_usage_data

def generate_yearly_report(year, include_revisions=True):
    '''If not already present, generate a yearly report for the given year in xlsx and json format

    Arguments:
        year -- _description_

    Returns:
        filename {string} -- filename of the report in xlsx format
    '''    
    if year == today.year:
        filename = f'/tmp/yearly_cost_report_{year}{today.strftime("%U")}.xlsx'
    else:
        filename = f'/tmp/yearly_cost_report_{year}.xlsx'

    usage_data = get_usage_data(start_year=year, end_year=year, include_revisions=include_revisions)
    print(usage_data)
    billing = get_billable_data(year, usage_data)
    usage = yearly_usage_formatted(year, billing)
    
    with open(f'{filename[:-5]}.json', 'w') as fp:
        json.dump(billing, fp)
    
    columns = ['project', 'created', 'deleted', 'owner_name', 'owner_vunetid', 'owner_email', 'budget_code', 'budget_type', 'budget_holder', 'active_cost', 'calculated_by_last']
    dfb = pd.DataFrame.from_dict(data=billing, orient='index', columns=columns)
    
    dfu = pd.DataFrame.from_dict(data=usage, orient='index')
    
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    dfb.to_excel(writer, sheet_name='billing', index=False)
    for column in dfb:
        column_length = max(dfb[column].astype(str).map(len).max(), len(str(column)))
        col_idx = dfb.columns.get_loc(column)
        writer.sheets['billing'].set_column(col_idx, col_idx, column_length)
    dfu.to_excel(writer, sheet_name='usage', index=False)
    for column in dfu:
        column_length = max(dfu[column].astype(str).map(len).max(), len(str(column)))
        col_idx = dfu.columns.get_loc(column)
        writer.sheets['usage'].set_column(col_idx, col_idx, column_length)
    writer.close()
    return filename
