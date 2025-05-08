from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('superadmin', 'Super Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='admin')
    is_active = models.BooleanField(default=True)  # trạng thái khóa/mở khóa
    employee_code = models.CharField(max_length=20, unique=True,  blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    cccd = models.CharField(max_length=12, unique=True,null=True, blank=True)

    def save(self, *args, **kwargs):
        # Chỉ sinh employee_code nếu chưa có mã nhân viên
        if not self.employee_code:
            last_user = User.objects.all().order_by('id').last()
            if last_user:
                # Lấy số thứ tự cuối cùng và tăng lên 1
                last_employee_number = int(last_user.employee_code[2:])
                new_employee_number = last_employee_number + 1
            else:
                # Nếu là người dùng đầu tiên thì bắt đầu từ 001
                new_employee_number = 1

            # Tạo employee_code với định dạng NV001, NV002, NV003...
            self.employee_code = f"NV{new_employee_number:03}"

        super().save(*args, **kwargs)