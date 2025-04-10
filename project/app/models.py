# 2222/project/app/models.py
from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    # 新增 type 字段，使用 CharField 并设置 choices 参数
    TYPE_CHOICES = [
        ('text', '文本'),
        ('image', '图像'),
        ('audio', '音频'),
        ('video', '视频'),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='text')


class ProjectFile(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    file_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, default='待处理')
    processed_at = models.DateTimeField(null=True, blank=True)
    local_path = models.CharField(max_length=255, null=True, blank=True)

class TextProcessingResult(models.Model):
    project_file = models.OneToOneField(ProjectFile, on_delete=models.CASCADE)
    result = models.JSONField()
    layout_dets = models.JSONField(null=True, blank=True)
    page_info = models.JSONField(null=True, blank=True)

class ImageProcessingResult(models.Model):
    project_file = models.OneToOneField(ProjectFile, on_delete=models.CASCADE)
    result = models.JSONField()
    predicted_label = models.CharField(max_length=255, null=True, blank=True)
    detection_results = models.JSONField(null=True, blank=True)

class AudioProcessingResult(models.Model):
    project_file = models.OneToOneField(ProjectFile, on_delete=models.CASCADE)
    result = models.JSONField()
    transcription = models.TextField(null=True, blank=True)
    mfccs = models.JSONField(null=True, blank=True)
    spectral_centroids = models.JSONField(null=True, blank=True)
    spectral_bandwidth = models.JSONField(null=True, blank=True)
    spectral_flatness = models.JSONField(null=True, blank=True)

class VideoProcessingResult(models.Model):
    project_file = models.OneToOneField(ProjectFile, on_delete=models.CASCADE)
    result = models.JSONField()
    action_result = models.JSONField(null=True, blank=True)