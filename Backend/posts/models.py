from django.db import models
from django.conf import settings

# Create your models here.
class Post(models.Model):
    """
    일반 게시글
    스터디 구성원이 작성하는 자유 게시판
    """
    study = models.ForeignKey(
        "studies.Study",
        on_delete=models.CASCADE,
        related_name="posts"
        )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts"
        )
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Notice(models.Model):
    """
    공지사항
    스터디 리더 혹은 관리자만 작성 가능
    """
    study = models.ForeignKey(
        "studies.Study",
        on_delete=models.CASCADE,
        related_name="notices"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notices"
    )
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class UploadedImage(models.Model):
    """
    공지사항/게시글에서 업로드된 이미지
    """
    image = models.ImageField(upload_to="post/images/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
