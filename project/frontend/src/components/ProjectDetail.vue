<template>
    <div class="project-detail-container">
        <!-- 路径栏 -->
        <div class="path-bar">
            <router-link :to="{ path: `/project/${projectName}` }"> / {{ projectName }}</router-link>
            <div class="button-group">
                <button @click="batchDeleteFiles" class="action-button">批量删除</button>
                <button @click="batchProcessFiles" class="action-button">批量处理</button>
            </div>
            <button @click="showUploadDialog = true" class="upload-button">上传</button>
        </div>
        <!-- 上传文件弹窗 -->
        <div v-if="showUploadDialog" class="upload-dialog">
            <div class="dialog-content">
                <h3>上传文件</h3>
                <!-- 选择文件区域 -->
                <div class="upload-file-section" @click="openFileDialog('single')">
                    <input
                        type="file"
                        ref="fileInputSingle"
                        @change="handleFileChange('single')"
                        multiple
                        :accept="allowedFileTypes"
                        style="display: none;"
                    />
                    <span>选择文件</span>
                </div>
                <!-- 选择文件夹区域 -->
                <div class="upload-folder-section" @click="openFileDialog('folder')">
                    <input
                        type="file"
                        ref="fileInputFolder"
                        @change="handleFileChange('folder')"
                        multiple
                        webkitdirectory
                        directory
                        style="display: none;"
                    />
                    <span>选择文件夹</span>
                </div>
                <p v-if="selectedFiles.length > 0">已选择文件: {{ selectedFiles.length === 1 ? selectedFiles[0].name : selectedFiles[0].name + ' 等 ' + selectedFiles.length + ' 个文件' }}</p>
                <p v-if="invalidFiles.length > 0" style="color: red;">以下文件类型不允许上传，将仅上传允许的文件: {{ invalidFiles.join(', ') }}</p>
                <button @click="uploadFiles">确认上传</button>
                <button @click="showUploadDialog = false">取消</button>
            </div>
        </div>

         <!-- 批量处理弹窗 -->
         <div v-if="isProcessing" class="processing-dialog">
            <div class="dialog-content">
                <h3>正在处理中...</h3>
                <progress :value="processedFiles" :max="totalFiles"></progress>
                <p>{{ processedFiles }} / {{ totalFiles }}</p>
            </div>
        </div>

        <!-- 灰色细线 -->
        <div class="path-bar-divider"></div>

        <div v-if="projectFiles.length > 0" class="file-list-container">
            <!-- 表头 -->
            <div class="file-list-header">
                <div class="header-item narrow-item center-item">
                    <input type="checkbox" v-model="isAllChecked" @change="toggleAllCheckboxes">
                </div>
                <div class="header-item narrow-item center-item">编号</div>
                <div class="header-item wide-item center-item">名称</div>
                <div class="header-item narrow-item center-item">状态</div>
                <div class="header-item narrow-item center-item">执行时间</div>
                <div class="header-item center-item"></div>
            </div>
            <!-- 文件列表 -->
            <div v-for="(file, index) in projectFiles" :key="file.id" class="file-list-row" :class="{ 'gray-row': index % 2 === 1 }">
                <div class="file-item narrow-item center-item">
                    <input type="checkbox" v-model="file.isChecked">
                </div>
                <div class="file-item narrow-item center-item">{{ index + 1 }}</div>
                <div class="file-item wide-item">{{ file.name }}</div>
                <div class="file-item narrow-item center-item">{{ file.status || '待处理' }}</div>
                <div class="file-item narrow-item center-item">{{ file.processed_at || '' }}</div>
                <div class="file-item center-item">
                    <div class="button-container">
                        <button @click="deleteFile(file.id)" class="action-button">删除</button>
                        <!-- 传递文件编号和名称给 FileDetail 组件 -->
                        <button @click="viewFileDetails(file.id, file.name, index)" class="action-button">查看详情</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    name: 'ProjectDetail',
    props: ['projectName', 'projectType'],
    data() {
        return {
            projectFiles: [],
            showUploadDialog: false,
            selectedFiles: [],
            invalidFiles: [],
            // 根据项目类型动态设置允许的文件类型
            allowedFileTypes: '.txt,.pdf,.doc,.docx,.csv,.jpg,.jpeg,.png,.wav,.mp3,.aac,.mp4',
            isUploading: false,
            uploadError: null,
            deleteFileUrl: 'http://127.0.0.1:8000/api/delete_file/',
            isAllChecked: false,
            isProcessing: false,
            totalFiles: 0,
            processedFiles: 0
        };
    },
    mounted() {
        this.getProjectFiles();
    },
    methods: {
        getProjectFiles() {
            axios.get(`http://127.0.0.1:8000/api/get_project_files/${this.projectName}/`)
              .then((response) => {
                    this.projectFiles = response.data.files.map(file => ({ ...file, isChecked: false }));
                })
              .catch((error) => {
                    console.error('获取项目文件列表失败:', error);
                });
        },
        deleteFile(fileId) {
            if (confirm('确定要删除该文件吗？')) {
                axios.post(`${this.deleteFileUrl}${fileId}/`)
                  .then((response) => {
                        console.log('文件删除成功:', response.data);
                        // 刷新文件列表
                        this.getProjectFiles();
                    })
                  .catch((error) => {
                        console.error('文件删除失败:', error);
                        alert('文件删除失败，请稍后重试。');
                    });
            }
        },
        viewFileDetails(fileId, filename, index) {
            const path = `/project/${this.projectName}/${filename}`;
            // 将文件编号作为查询参数传递给 FileDetail 组件
            this.$router.push({ path, query: { index } });
        },
        // 根据项目类型返回允许的文件类型字符串
        getAllowedFileTypes() {
            switch (this.projectType) {
                case 'text':
                    this.allowedFileTypes = '.txt,.pdf,.doc,.docx,.csv';
                    break;
                case 'image':
                    this.allowedFileTypes = '.jpg,.jpeg,.png';
                    break;
                case 'audio':
                    this.allowedFileTypes =  '.wav,.mp3';
                    break;
                case 'video':
                    this.allowedFileTypes = '.aac,.mp4';
                    break;
                default:
                    this.allowedFileTypes = '.txt,.pdf,.doc,.docx,.csv';
            }
        },
        openFileDialog(type) {
            if (type === 'single') {
                this.$refs.fileInputSingle.click();
            } else if (type === 'folder') {
                this.$refs.fileInputFolder.click();
            }
        },
        handleFileChange(type) {
            let files;
            if (type === 'single') {
                files = Array.from(this.$refs.fileInputSingle.files);
            } else if (type === 'folder') {
                files = Array.from(this.$refs.fileInputFolder.files);
            }

            this.selectedFiles = [];
            this.invalidFiles = [];

            // 过滤允许的文件
            files.forEach((file) => {
                const fileExtension = `.${file.name.split('.').pop().toLowerCase()}`;
                if (this.allowedFileTypes.includes(fileExtension)) {
                    this.selectedFiles.push(file);
                } else {
                    this.invalidFiles.push(file.name);
                }
            });
        },
        uploadFiles() {
            if (this.isUploading) return;
            this.isUploading = true;
            this.uploadError = null;

            const formData = new FormData();
            this.selectedFiles.forEach((file) => {
                formData.append('files', file);
            });

            axios.post(`http://127.0.0.1:8000/api/upload_files/${this.projectName}/`, formData, {
                headers: {
                    // 不要手动设置 Content-Type
                }
            })
              .then((response) => {
                    console.log('文件上传成功:', response.data);
                    this.showUploadDialog = false;
                    this.selectedFiles = [];
                    this.invalidFiles = [];
                    this.getProjectFiles();
                })
              .catch((error) => {
                    console.error('文件上传失败:', error);
                    this.uploadError = error.response?.data?.message || '上传文件时发生未知错误';
                })
              .finally(() => {
                    this.isUploading = false;
                });
        },
        toggleAllCheckboxes() {
            this.projectFiles.forEach(file => file.isChecked = this.isAllChecked);
        },
        batchProcessFiles() {
            const selectedFileIds = this.projectFiles.filter(file => file.isChecked).map(file => file.id);
            if (selectedFileIds.length === 0) {
                alert('请选择要处理的文件');
                return;
            }
            this.isProcessing = true;
            this.totalFiles = selectedFileIds.length;
            this.processedFiles = 0;

            const formData = new FormData();
            selectedFileIds.forEach(fileId => {
                formData.append('file_ids', fileId);
            });

            const eventSource = new EventSource(`http://127.0.0.1:8000/api/batch_process_files/?${new URLSearchParams({
                file_ids: selectedFileIds
            })}`);

            eventSource.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'progress') {
                    this.processedFiles = data.processed;
                } else if (data.type === 'finished') {
                    eventSource.close();
                    this.isProcessing = false;
                    this.getProjectFiles();
                }
            };

            eventSource.onerror = (error) => {
                console.error('批量处理失败:', error);
                eventSource.close();
                this.isProcessing = false;
                alert('批量处理失败，请稍后重试。');
            };
        },
        batchDeleteFiles() {
            const selectedFileIds = this.projectFiles.filter(file => file.isChecked).map(file => file.id);
            if (selectedFileIds.length === 0) {
                alert('请选择要删除的文件');
                return;
            }
            if (confirm('确定要批量删除这些文件吗？')) {
                const formData = new FormData();
                selectedFileIds.forEach(fileId => {
                    formData.append('file_ids', fileId);
                });
                axios.post('http://127.0.0.1:8000/api/batch_delete_files/', formData)
                  .then((response) => {
                        console.log('批量删除成功:', response.data);
                        // 刷新文件列表
                        this.getProjectFiles();
                    })
                  .catch((error) => {
                        console.error('批量删除失败:', error);
                        alert('批量删除失败，请稍后重试。');
                    });
            }
        }
    }
};
</script>

<style scoped>
.project-detail-container {
    padding: 0px;
}

.file-list-container {
    width: 100%;
}

.file-list-header {
    display: flex;
    font-weight: bold;
    padding: 10px 0;
    border-bottom: 1px solid #e0e0e0;
}

.file-list-row {
    display: flex;
    align-items: center;
    padding: 10px 0;
}

.header-item,
.file-item {
    flex: 1;
}

/* 窄列样式 */
.narrow-item {
    flex: 0 0 100px;
}

/* 宽列样式 */
.wide-item {
    flex: 2;
}

/* 居中显示 */
.center-item {
    text-align: center;
}

.gray-row {
    background-color: #f5f5f5;
}

.action-button {
    padding: 5px 10px;
    margin-right: 5px;
    border: none;
    background-color: #007bff;
    color: white;
    border-radius: 3px;
    cursor: pointer;
}

.action-button:hover {
    background-color: #0056b3;
}

/* 按钮容器居中 */
.button-container {
    display: flex;
    justify-content: center;
}

/* 路径栏样式 */
.path-bar {
    margin-bottom: 10px;
    font-size: 14px;
    color: #666;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.path-bar a {
    color: #007bff;
    text-decoration: none; /* 取消下划线 */
}

.path-bar a:hover {
    text-decoration: underline; /* 鼠标悬停时显示下划线 */
}

.upload-button {
    padding: 5px 10px;
    border: none;
    background-color: #007bff;
    color: white;
    border-radius: 3px;
    cursor: pointer;
}

.upload-button:hover {
    background-color: #0056b3;
}

/* 路径栏分隔线 */
.path-bar-divider {
    border-bottom: 1px solid #ccc;
    margin-bottom: 10px;
    width: 100%;
}

.upload-dialog {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
}

.dialog-content {
    background-color: white;
    padding: 20px;
    border-radius: 5px;
    text-align: center;
}

.upload-file-section,
.upload-folder-section {
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 20px;
    margin: 10px;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

.upload-file-section:hover,
.upload-folder-section:hover {
    background-color: #f0f0f0;
}

.button-group {
    display: flex;
}

.processing-dialog {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
}
.dialog-content {
    background-color: white;
    padding: 20px;
    border-radius: 5px;
    text-align: center;
}
</style>