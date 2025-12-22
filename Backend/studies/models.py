from django.db import models
from django.conf import settings
import random, string

# Create your models here.
class Study(models.Model):
    name = models.CharField(max_length=40)
    leader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through = 'StudyMembership',
        related_name='joined_studies'
    )
    created_at = models.DateTimeField(auto_now_add=True)

class StudyMembership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='study_membership', on_delete=models.CASCADE)
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20,
        choices = [('leader', '리더'), ('admin', '관리자'), ('member', '그룹원')],
        default = 'member'
    )
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "study"],
                name = "unique_user_study"
            )
        ]

class CodeBlackList(models.Model):
    join_code = models.CharField(max_length=12)

class StudyJoinCode(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    join_code = models.CharField(max_length=12, unique=True, blank=True, null=True)
    
    def generate_random_code(self, length=12):
        """랜덤 코드 생성"""
        characters = string.ascii_letters + string.digits   # 대소문자와 숫자를 포함한 문자열
        return ''.join(random.choice(characters) for _ in range(length))

    def save(self, *args, **kwargs):
        """저장 전, join_code가 유니크한 지 확인하고 랜덤 코드 생성"""
        if not self.join_code:
            # 랜덤 코드를 생성
            while True:
                random_code = self.generate_random_code()
                # 생성된 코드가 데이터베이스에 존재하는 지 확인
                if not CodeBlackList.objects.filter(join_code=random_code).exists():
                    self.join_code = random_code
                    break
        CodeBlackList.objects.create(join_code = self.join_code)
        super().save(*args, **kwargs)
    
    def update_join_code(self):
        """코드 갱신"""
        while True:
            random_code = self.generate_random_code()
            # 생성된 코드가 데이터베이스에 존재하는 지 확인
            if not CodeBlackList.objects.filter(join_code=random_code).exists():
                self.join_code = random_code
                break
        CodeBlackList.objects.create(join_code = self.join_code)
        super().save()