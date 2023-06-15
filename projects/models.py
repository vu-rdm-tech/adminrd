from django.db import models

# Create your models here.
   

class User(models.Model):
    rdid = models.IntegerField()
    username = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100, blank=True)
    backend = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    last_login = models.DateTimeField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}'
    

class Department(models.Model):
    name = models.CharField(max_length=255, blank=True)
    abbreviation = models.CharField(max_length=255, blank=True)
    faculty = models.CharField(max_length=255, blank=True)
    institute = models.CharField(max_length=255, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['abbreviation', 'faculty'], name='unique_abbreviation_faculty')
        ]

    def __str__(self):
        return f'{self.faculty}-{self.abbreviation}'


class Budget(models.Model):
    CODE_TYPES = (
        ('w', 'WBS-Element'),
        ('o', 'Order Number'),
        ('c', 'Cost Center item number'),
        ('u', 'unknown'),
    )
    code = models.CharField(max_length=50)  # check this
    type = models.CharField(max_length=1, choices=CODE_TYPES)
    vunetid = models.CharField(max_length=6)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['code'], name='unique_code')
        ]

    def __str__(self):
        return self.code


class Project(models.Model):
    rdid = models.IntegerField()
    name = models.CharField(max_length=255)
    description = models.TextField()
    
    owner_name = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, null=True)
    
    create_date = models.DateTimeField()
    change_date = models.DateTimeField(null=True)
    last_update = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)

    quotum = models.IntegerField(default=10)
    
    admin_remarks = models.TextField(default='', blank=True)

    internal_users = models.IntegerField(default=1)
    external_users = models.IntegerField(default=0)

    delete_date = models.DateField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class MiscStats(models.Model):
    size_total = models.DecimalField(max_digits=8, decimal_places=2)
    quotum_total = models.BigIntegerField(default=0)
    users_total = models.IntegerField(default=0)
    internal_users_total = models.IntegerField(default=0)
    external_users_total = models.IntegerField(default=0)
    projects_total = models.IntegerField(default=6)
    collected = models.DateField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'collected - {self.collected}'


class ProjectStats(models.Model):
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, blank=True, null=True)
    size = models.DecimalField(max_digits=8, decimal_places=2)
    quotum = models.IntegerField()
    collected = models.DateField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.project.name} - {self.collected}'