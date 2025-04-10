<template>
  <div class="file-detail-container">
    <!-- 新的顶部栏 -->
    <div class="file-detail-top-bar">
      <div class="path-bar">
        <router-link :to="{ path: `/project/${projectName}` }"> / {{ projectName }}</router-link>
        / {{ filename }}
      </div>
      <div class="navigation-buttons">
        <button @click="toggleEditMode" class="action-button" :class="{ 'save-button': isEditMode }">
          {{ isEditMode ? '保存' : '编辑' }}
        </button>
        <button :disabled="isFirstFile" @click="prevFile" class="action-button">上一个</button>
        <button :disabled="isLastFile" @click="nextFile" class="action-button">下一个</button>
      </div>
    </div>
    <!-- 灰色细线 -->
    <div class="path-bar-divider"></div>

    <!-- 灰线以下部分 -->
    <div class="content-container">
      <!-- 左侧文件列表 -->
      <div class="file-list-container">
        <div class="file-list">
          <div v-for="(file, index) in projectFiles" :key="file.id" @click="viewFileDetails(file.id, file.name, index)" class="file-item">
            {{ file.name }}
          </div>
        </div>
      </div>
      <!-- 中间文件预览区域 -->
      <div class="file-preview-container">
        <!-- 文件预览区域 -->
        <div v-if="previewUrl">
          <div v-if="isTextFile">
            <pre>{{ textContent }}</pre>
          </div>
          <div v-else-if="isImageFile" class="image-preview-container">
            <div class="image-controls">
              <button @click="zoomIn" class="control-button">放大</button>
              <button @click="zoomOut" class="control-button">缩小</button>
              <button @click="rotateLeft" class="control-button">向左旋转</button>
              <button @click="rotateRight" class="control-button">向右旋转</button>
              <button @click="resetImage" class="control-button">重置</button>
            </div>
            <div class="image-wrapper" 
                 @wheel.prevent="handleWheel"
                 @mousedown="startDrag"
                 @mousemove="onDrag"
                 @mouseup="stopDrag"
                 @mouseleave="stopDrag">
              <img 
                ref="imageRef"
                :src="previewUrl" 
                alt="预览图" 
                :style="{
                  transform: `translate(${translateX}px, ${translateY}px) scale(${scale}) rotate(${rotation}deg)`,
                  cursor: isDragging && !isEditingBox ? 'grabbing' : (isEditingBox ? 'move' : 'grab')
                }"
                @dragstart.prevent
                @load="onImageLoad"
              >
            </div>
          </div>
          <div v-else-if="isAudioFile" class="centered-content">
            <audio controls :src="previewUrl"></audio>
          </div>
          <div v-else-if="isVideoFile" class="centered-content">
            <video controls :src="previewUrl" style="max-width: 100%;"></video>
          </div>
          <div v-else-if="isPdfFile">
            <embed :src="previewUrl" type="application/pdf" width="100%" height="600px" />
          </div>
          <div v-else>
            <a :href="previewUrl" download>下载文件</a>
          </div>
        </div>
      </div>
      <!-- 右侧分隔线 -->
      <div class="divider"></div>
      <!-- 右侧解析结果区域 -->
      <div class="analysis-result-container">
        <!-- 新增顶部栏 -->
        <div class="result-top-bar fixed-top">
          <button v-if="isPdfFile" @click="selectedTab = 'layout_dets'">文本</button>
          <button v-if="isPdfFile" @click="selectedTab = 'figures'">图片</button>
          <button v-if="isPdfFile" @click="selectedTab = 'tables'">表格</button>
          <button v-if="isPdfFile" @click="selectedTab = 'formulas'">公式</button>
          <button v-if="isPdfFile" @click="selectedTab = 'page_info'">页面属性</button>
          <button v-if="isImageFile" @click="selectedTab = 'predicted_label'">图片标签</button>
          <button v-if="isImageFile" @click="selectedTab = 'detection_results'">目标检测</button>
          <button v-if="isAudioFile" @click="selectedTab = 'transcription'">语音识别</button>
          <button v-if="isAudioFile" @click="selectedTab = 'mfccs'">MFCC特征</button>
          <button v-if="isAudioFile" @click="selectedTab = 'spectral_centroids'">频谱中心频率</button>
          <button v-if="isAudioFile" @click="selectedTab = 'spectral_bandwidth'">频谱带宽</button>
          <button v-if="isAudioFile" @click="selectedTab = 'spectral_flatness'">频谱平坦度</button>
          <button v-if="isVideoFile" @click="selectedTab = 'action_result'">动作识别</button>
        </div>
        <!-- 解析结果内容 -->
        <div v-if="processingResult">
          <!-- 图片展示区域 -->
          <div v-if="isPdfFile && selectedTab === 'figures'" class="figures-container">
            <div v-if="hasFigures" class="figures-grid">
              <div v-for="(figure, index) in extractedFigures" :key="index" class="figure-item">
                <div class="figure-preview">
                  <img :src="figure.image_url" :alt="'图片 ' + (index + 1)" class="figure-image">
                </div>
                <div class="figure-caption" v-if="figure.caption">
                  {{ figure.caption }}
                </div>
              </div>
            </div>
            <div v-else class="no-data-message">未识别到图片</div>
          </div>

          <!-- 公式展示区域 -->
          <div v-if="isPdfFile && selectedTab === 'formulas'" class="formulas-container">
            <div v-if="hasFormulas" class="formulas-list">
              <div v-for="(formula, index) in extractedFormulas" :key="index" class="formula-item">
                <div class="formula-latex">
                  <div class="latex-render" v-html="renderLatex(formula.latex)"></div>
                </div>
                <div class="formula-caption" v-if="formula.caption">
                  {{ formula.caption }}
                </div>
              </div>
            </div>
            <div v-else class="no-data-message">未识别到公式</div>
          </div>
          <div v-else-if="isImageFile && selectedTab === 'predicted_label'" class="detection-results">
            <div class="detection-item">
              <span v-if="!isEditMode" class="label">{{ processingResult.predicted_label }}</span>
              <input v-else
                     type="text"
                     class="label-input"
                     :value="editedPredictedLabel || processingResult.predicted_label"
                     @input="handlePredictedLabelEdit"
                     placeholder="输入图片标签" />
            </div>
          </div>
          <div v-else-if="isPdfFile && selectedTab === 'layout_dets'" class="layout-results">
            <div v-if="processingResult.layout_dets && processingResult.layout_dets.length > 0">
              <div>
                <div v-if="filteredCurrentPageLayoutItems.length > 0">
                  <div v-for="(item, index) in filteredCurrentPageLayoutItems" :key="`${currentPdfPage}-${index}`" class="layout-item" :class="item.category_type">
                    <div class="layout-header">
                      <span v-if="!isEditMode" class="layout-type">{{ getTypeDisplayName(item.category_type) }}</span>
                      <select v-else class="layout-type-select" v-model="item.category_type" @change="handleLayoutTypeChange(currentPdfPage, index, $event)">
                        <option v-for="(displayName, typeName) in layoutTypeOptions" :key="typeName" :value="typeName">
                          {{ displayName }}
                        </option>
                      </select>
                      <span class="layout-confidence" v-if="item.score">置信度: {{ item.score.toFixed(2) }}</span>
                    </div>
                    <div class="layout-content">
                      <template v-if="!isEditMode">
                        <p v-if="item.text && item.category_type !== 'title'" class="content-text">{{ item.text }}</p>
                        <h3 v-if="item.text && item.category_type === 'title'" class="content-title">{{ item.text }}</h3>
                      </template>
                      
                      <template v-else>
                        <textarea 
                          v-if="item.text && item.category_type !== 'title'" 
                          class="content-text-edit"
                          v-model="item.text"
                          @input="handleLayoutTextEdit(currentPdfPage, index, $event)"
                        ></textarea>
                        <input 
                          v-if="item.text && item.category_type === 'title'" 
                          class="content-title-edit"
                          v-model="item.text"
                          @input="handleLayoutTextEdit(currentPdfPage, index, $event)"
                        />
                      </template>
                      
                      <div v-if="item.category_type === 'list' && item.text" class="content-list">
                        <template v-if="!isEditMode">
                          <ul>
                            <li v-for="(line, lineIndex) in item.text.split('\n').filter(l => l.trim())" :key="lineIndex">
                              {{ line.replace(/^[\s•\-\*]+/, '') }}
                            </li>
                          </ul>
                        </template>
                        <textarea 
                          v-else 
                          class="content-list-edit"
                          v-model="item.text"
                          @input="handleLayoutTextEdit(currentPdfPage, index, $event)"
                        ></textarea>
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else class="no-data-message">该页面无文本数据</div>
              </div>
            </div>
            <div v-else class="no-data-message">无页面布局数据</div>
            
            <div class="page-selector">
              <button 
                @click="prevPage" 
                :disabled="currentPdfPage <= 0"
                class="page-button"
              >
                上一页
              </button>
              <select 
                v-model="currentPdfPage" 
                class="page-select"
              >
                <option 
                  v-for="(_, index) in processingResult?.layout_dets || []" 
                  :key="index" 
                  :value="index"
                >
                  {{ index + 1 }}
                </option>
              </select>
              <span class="page-count">/ {{ processingResult?.layout_dets?.length || 0 }}</span>
              <button 
                @click="nextPage" 
                :disabled="currentPdfPage >= (processingResult?.layout_dets?.length - 1 || 0)"
                class="page-button"
              >
                下一页
              </button>
            </div>
          </div>
          <div v-else-if="isPdfFile && selectedTab === 'tables'" class="tables-container">
            <div v-if="extractedTables.length > 0" class="tables-list">
              <div v-for="(table, index) in extractedTables" :key="index" class="table-item">
                <div class="table-header">
                  <span class="table-label">表格 {{ index + 1 }}</span>
                  <span class="table-page">第 {{ table.page }} 页</span>
                </div>
                <div class="table-content">
                  <table>
                    <tbody>
                      <tr v-for="(row, rowIndex) in table.content" :key="rowIndex">
                        <td v-for="(cell, cellIndex) in row" :key="cellIndex">
                          {{ cell }}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div class="table-caption" v-if="table.caption">
                  {{ table.caption }}
                </div>
              </div>
            </div>
            <div v-else class="no-data-message">未识别到表格</div>
          </div>
          <div v-else-if="isPdfFile && selectedTab === 'page_info'" class="page-info">
            <div v-for="(pageInfo, pageIndex) in processingResult.page_info" :key="pageIndex">
              <div class="page-divider">————————第{{ pageIndex + 1 }}页————————</div>
              <div class="page-info-content">
                <div class="info-item">
                  <span class="info-label">宽度：</span>
                  <span class="info-value">{{ pageInfo.width }}px</span>
                </div>
                <div class="info-item">
                  <span class="info-label">高度：</span>
                  <span class="info-value">{{ pageInfo.height }}px</span>
                </div>
              </div>
            </div>
          </div>
          <pre v-else-if="(isPdfFile || isImageFile || isAudioFile || isVideoFile) && selectedTab in processingResult" class="result-content">
            {{ JSON.stringify(processingResult[selectedTab], null, 2) }}
          </pre>
        </div>
        <p v-else>解析结果区域</p>
      </div>
    </div>
  </div>
</template>

<script>
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { ref, onMounted, watch, nextTick, onBeforeUnmount, computed } from 'vue';
import VueEasyLightbox from 'vue-easy-lightbox';
import katex from 'katex';
import 'katex/dist/katex.min.css';

export default {
  name: 'FileDetail',
  components: {
    VueEasyLightbox
  },
  setup() {
    const route = useRoute();
    const router = useRouter();
    const projectName = route.params.projectname;
    const filename = route.params.filename;
    const currentIndex = parseInt(route.query.index);
    const project = ref(null);
    const previewUrl = ref('');
    const textContent = ref('');
    const isTextFile = ref(false);
    const isImageFile = ref(false);
    const isAudioFile = ref(false);
    const isVideoFile = ref(false);
    const isPdfFile = ref(false);
    const projectFiles = ref([]);
    const processingResult = ref(null);
    const selectedTab = ref('');
    const currentPdfPage = ref(0);
    const visible = ref(false);
    const index = ref(0);
    const imgs = ref([]);
    const scale = ref(1);
    const rotation = ref(0);
    const isDragging = ref(false);
    const startX = ref(0);
    const startY = ref(0);
    const translateX = ref(0);
    const translateY = ref(0);
    const imageRef = ref(null);
    const selectedBoxIndex = ref(-1);
    const isEditingBox = ref(false);
    const editingPoint = ref(-1);
    const canvasRef = ref(null);
    const canvasCtx = ref(null);
    const boxColors = ref([]);
    const labelColorMap = ref(new Map());
    const isEditMode = ref(false);
    const editedLabels = ref(new Map());
    const editedPredictedLabel = ref('');
    const hasUnsavedChanges = ref(false);

    // 获取布局类型的显示名称
    const getTypeDisplayName = (type) => {
      const typeMap = {
        'title': '标题',
        'plain_text': '文本',
        'figure': '图片',
        'figure_caption': '图片标题',
        'table': '表格',
        'table_caption': '表格标题',
        'table_footnote': '表格脚注',
        'isolated_formula': '公式',
        'formula_caption': '公式标题',
        'abandoned_text': '其他',
      };
      return typeMap[type] || type;
    };

    // 使用 typeMap 替代 layoutTypeOptions
    const layoutTypeOptions = computed(() => {
      const typeMap = {
        'title': '标题',
        'plain_text': '文本',
        'figure': '图片',
        'figure_caption': '图片标题',
        'table': '表格',
        'table_caption': '表格标题',
        'table_footnote': '表格脚注',
        'isolated_formula': '公式',
        'formula_caption': '公式标题',
        'abandoned_text': '其他',
      };
      return typeMap;
    });

    // 计算当前页面的布局元素
    const currentPageLayoutDets = computed(() => {
      if (processingResult.value && processingResult.value.layout_dets && 
          processingResult.value.layout_dets.length > currentPdfPage.value) {
        return processingResult.value.layout_dets[currentPdfPage.value];
      }
      return [];
    });

    // 格式化表格数据
    const formatTableData = (item) => {
      // 如果有结构化表格数据，直接使用
      if (item.structured_content && Array.isArray(item.structured_content)) {
        return item.structured_content;
      }
      
      // 否则尝试从文本中解析表格
      if (item.text) {
        try {
          // 按行分割，然后按制表符(\t)分割每行
          const rows = item.text.split('\n').filter(row => row.trim());
          return rows.map(row => row.split('\t').filter(cell => cell.trim()));
        } catch (e) {
          console.error('解析表格失败:', e);
          return [['无法解析表格数据']];
        }
      }
      
      return [['无数据']];
    };
    
    // 计算图形的宽高比
    const getFigureAspectRatio = (poly) => {
      if (!poly || poly.length < 8) return '1/1';
      
      // 使用poly坐标计算宽高比 [x1,y1,x2,y2,x3,y3,x4,y4]
      const x1 = poly[0];
      const y1 = poly[1];
      const x2 = poly[2];
      const y2 = poly[3];
      const x3 = poly[4];
      const y3 = poly[5];
      const x4 = poly[6];
      const y4 = poly[7];
      
      // 计算宽度和高度
      const width = Math.max(Math.abs(x2 - x1), Math.abs(x4 - x3));
      const height = Math.max(Math.abs(y3 - y1), Math.abs(y4 - y2));
      
      return `${width}/${height}`;
    };

    // 生成随机颜色
    const generateRandomColor = () => {
      const hue = Math.floor(Math.random() * 360);
      return `hsl(${hue}, 70%, 50%)`;
    };

    // 获取标签对应的颜色
    const getLabelColor = (label) => {
      if (!labelColorMap.value.has(label)) {
        labelColorMap.value.set(label, generateRandomColor());
      }
      return labelColorMap.value.get(label);
    };

    // 监听标签切换，当切换到目标检测时绘制检测框
    watch(selectedTab, (newTab) => {
      if (newTab === 'detection_results' && isImageFile.value && processingResult.value && processingResult.value.detection_results) {
        nextTick(() => {
          // 为每个检测框生成颜色（基于标签）
          boxColors.value = processingResult.value.detection_results.map(result => getLabelColor(result.label));
          drawDetectionBoxes();
        });
      } else {
        clearDetectionBoxes();
      }
    });

    // 监听图像变换，重新绘制检测框
    watch([scale, rotation, translateX, translateY], () => {
      if (selectedTab.value === 'detection_results') {
        drawDetectionBoxes();
      }
    });

    // 修改绘制检测框函数
    const drawDetectionBoxes = () => {
      if (!canvasRef.value || !canvasCtx.value || !imageRef.value || !processingResult.value || !processingResult.value.detection_results) return;
      
      const canvas = canvasRef.value;
      const ctx = canvasCtx.value;
      const img = imageRef.value;
      
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      processingResult.value.detection_results.forEach((result, index) => {
        const bbox = result.bbox;
        const [x1, y1, x2, y2] = bbox;
        
        const boxColor = boxColors.value[index] || '#00ff00';
        ctx.strokeStyle = index === selectedBoxIndex.value ? '#ff0000' : boxColor;
        ctx.lineWidth = 3;
        
        // 只有在选中状态下才填充底色
        if (index === selectedBoxIndex.value) {
          ctx.fillStyle = boxColor.replace(')', ', 0.1)').replace('hsl', 'hsla');
          ctx.fillRect(x1, y1, x2 - x1, y2 - y1);
        }
        
        // 始终绘制边框
        ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
        
        if (index === selectedBoxIndex.value && isEditMode.value) {
          drawControlPoints(x1, y1, x2, y2);
        }
      });
    };

    // 绘制控制点
    const drawControlPoints = (x1, y1, x2, y2) => {
      const ctx = canvasCtx.value;
      const points = [
        { x: x1, y: y1 }, // 左上
        { x: x2, y: y1 }, // 右上
        { x: x2, y: y2 }, // 右下
        { x: x1, y: y2 }  // 左下
      ];
      
      ctx.fillStyle = '#ffffff';
      ctx.strokeStyle = '#000000';
      ctx.lineWidth = 2;
      
      points.forEach((point) => {
        ctx.beginPath();
        ctx.arc(point.x, point.y, 5, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
      });
    };

    // 清除检测框
    const clearDetectionBoxes = () => {
      if (!canvasRef.value || !canvasCtx.value) return;
      
      const canvas = canvasRef.value;
      const ctx = canvasCtx.value;
      
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      selectedBoxIndex.value = -1;
      isEditingBox.value = false;
      editingPoint.value = -1;
    };

    // 初始化画布
    const initCanvas = () => {
      if (!imageRef.value) return;
      
      const canvas = document.createElement('canvas');
      canvas.style.position = 'absolute';
      canvas.style.top = '0';
      canvas.style.left = '0';
      canvas.style.width = '100%';
      canvas.style.height = '100%';
      canvas.style.pointerEvents = 'none';
      canvas.style.zIndex = '10';
      
      const imageWrapper = document.querySelector('.image-wrapper');
      const oldCanvas = imageWrapper.querySelector('.detection-canvas');
      if (oldCanvas) {
        imageWrapper.removeChild(oldCanvas);
      }
      
      canvas.classList.add('detection-canvas');
      imageWrapper.appendChild(canvas);
      
      canvasRef.value = canvas;
      canvasCtx.value = canvas.getContext('2d');
      
      // 添加鼠标事件监听
      canvas.style.pointerEvents = 'auto';
      canvas.addEventListener('mousedown', handleCanvasMouseDown);
      canvas.addEventListener('mousemove', handleCanvasMouseMove);
      canvas.addEventListener('mouseup', handleCanvasMouseUp);
    };

    // 处理画布鼠标按下事件
    const handleCanvasMouseDown = (e) => {
      if (selectedTab.value !== 'detection_results' || !processingResult.value || !processingResult.value.detection_results) return;
      
      const rect = canvasRef.value.getBoundingClientRect();
      const scaleX = canvasRef.value.width / rect.width;
      const scaleY = canvasRef.value.height / rect.height;
      
      const x = (e.clientX - rect.left) * scaleX;
      const y = (e.clientY - rect.top) * scaleY;
      
      // 检查是否点击了控制点
      let foundPoint = false;
      let closestPoint = { index: -1, pointIndex: -1, distance: Infinity };
      
      for (let i = 0; i < processingResult.value.detection_results.length; i++) {
        const result = processingResult.value.detection_results[i];
        const bbox = result.bbox;
        const [x1, y1, x2, y2] = bbox;
        
        const points = [
          { x: x1, y: y1 }, // 左上
          { x: x2, y: y1 }, // 右上
          { x: x2, y: y2 }, // 右下
          { x: x1, y: y2 }  // 左下
        ];
        
        for (let j = 0; j < points.length; j++) {
          const point = points[j];
          const distance = Math.sqrt(Math.pow(x - point.x, 2) + Math.pow(y - point.y, 2));
          
          if (distance < 10) {
            foundPoint = true;
            // 记录最近的控制点
            if (distance < closestPoint.distance) {
              closestPoint = { index: i, pointIndex: j, distance };
            }
          }
        }
      }
      
      if (foundPoint) {
        // 使用最近的控制点
        selectedBoxIndex.value = closestPoint.index;
        isEditingBox.value = true;
        editingPoint.value = closestPoint.pointIndex;
      } else {
        // 如果没有点击任何控制点，取消选择
        selectedBoxIndex.value = -1;
        isEditingBox.value = false;
        editingPoint.value = -1;
      }
      
      drawDetectionBoxes();
    };

    // 处理画布鼠标移动事件
    const handleCanvasMouseMove = (e) => {
      if (!isEditingBox.value || selectedBoxIndex.value === -1 || !processingResult.value || !processingResult.value.detection_results) return;
      
      const rect = canvasRef.value.getBoundingClientRect();
      const scaleX = canvasRef.value.width / rect.width;
      const scaleY = canvasRef.value.height / rect.height;
      
      const x = (e.clientX - rect.left) * scaleX;
      const y = (e.clientY - rect.top) * scaleY;
      
      const result = processingResult.value.detection_results[selectedBoxIndex.value];
      const bbox = result.bbox;
      
      // 只有在拖动控制点时才移动
      if (editingPoint.value !== -1) {
        // 移动控制点
        if (editingPoint.value === 0) { // 左上角
          bbox[0] = x;
          bbox[1] = y;
        } else if (editingPoint.value === 1) { // 右上角
          bbox[2] = x;
          bbox[1] = y;
        } else if (editingPoint.value === 2) { // 右下角
          bbox[2] = x;
          bbox[3] = y;
        } else if (editingPoint.value === 3) { // 左下角
          bbox[0] = x;
          bbox[3] = y;
        }
        
        drawDetectionBoxes();
      }
    };

    // 处理画布鼠标松开事件
    const handleCanvasMouseUp = () => {
      isEditingBox.value = false;
    };

    // 监听图像加载完成事件
    const onImageLoad = () => {
      if (imageRef.value) {
        initCanvas();
        if (selectedTab.value === 'detection_results') {
          drawDetectionBoxes();
        }
      }
    };

    const prevFile = () => {
      // 检查是否有未保存的更改
      if (hasUnsavedChanges.value) {
        if (!confirm('您有未保存的更改，切换文件将丢失这些更改。是否保存？')) {
          // 用户选择不保存，重置更改
          resetChanges();
        } else {
          // 用户选择保存，先保存再切换
          toggleEditMode().then(() => {
            navigateToPrevFile();
          });
          return;
        }
      }
      
      navigateToPrevFile();
    };
    
    const navigateToPrevFile = () => {
      if (currentIndex > 0) {
        const prevIndex = currentIndex - 1;
        axios.get(`http://127.0.0.1:8000/api/get_projects/`)
          .then((response) => {
            const projects = response.data.projects;
            project.value = projects.find(p => p.name === projectName);
            if (project.value) {
              const prevFile = project.value.files[prevIndex];
              const path = `/project/${projectName}/${prevFile.name}`;
              router.push({ path, query: { index: prevIndex } });
            }
          })
          .catch((error) => {
            console.error('获取项目文件列表失败:', error);
          });
      }
    };

    const nextFile = () => {
      // 检查是否有未保存的更改
      if (hasUnsavedChanges.value) {
        if (!confirm('您有未保存的更改，切换文件将丢失这些更改。是否保存？')) {
          // 用户选择不保存，重置更改
          resetChanges();
        } else {
          // 用户选择保存，先保存再切换
          toggleEditMode().then(() => {
            navigateToNextFile();
          });
          return;
        }
      }
      
      navigateToNextFile();
    };
    
    const navigateToNextFile = () => {
      axios.get(`http://127.0.0.1:8000/api/get_projects/`)
        .then((response) => {
          const projects = response.data.projects;
          project.value = projects.find(p => p.name === projectName);
          if (project.value) {
            const nextIndex = currentIndex + 1;
            if (project.value.files && nextIndex < project.value.files.length) {
              const nextFile = project.value.files[nextIndex];
              const path = `/project/${projectName}/${nextFile.name}`;
              router.push({ path, query: { index: nextIndex } });
            }
          }
        })
        .catch((error) => {
          console.error('获取项目文件列表失败:', error);
        });
    };

    const viewFileDetails = (fileId, filename, index) => {
      const path = `/project/${projectName}/${filename}`;
      router.push({ path, query: { index } });
    };

    const isFirstFile = computed(() => currentIndex === 0);
    const isLastFile = computed(() => project.value && project.value.files && currentIndex === project.value.files.length - 1);

    // 添加页面导航功能
    const prevPage = () => {
      if (currentPdfPage.value > 0) {
        currentPdfPage.value -= 1;
      }
    };

    const nextPage = () => {
      if (processingResult.value && processingResult.value.layout_dets && 
          currentPdfPage.value < processingResult.value.layout_dets.length - 1) {
        currentPdfPage.value += 1;
      }
    };
    
    // 过滤当前页面的布局项，排除公式、图片和表格
    const filteredCurrentPageLayoutItems = computed(() => {
      if (processingResult.value && processingResult.value.layout_dets && 
          processingResult.value.layout_dets.length > currentPdfPage.value) {
        const currentPageItems = processingResult.value.layout_dets[currentPdfPage.value] || [];
        
        // 过滤掉公式、图片、表格相关的布局项
        return currentPageItems.filter(item => {
          const excludedTypes = ['isolated_formula', 'formula', 'figure', 'table', 'figure_caption', 'table_caption', 'formula_caption', 'table_footnote'];
          return !excludedTypes.includes(item.category_type);
        });
      }
      return [];
    });
    
    // 提取所有表格
    const extractedTables = computed(() => {
      if (!processingResult.value || !processingResult.value.layout_dets) return [];
      
      const tables = [];
      processingResult.value.layout_dets.forEach((pageItems, pageIndex) => {
        pageItems.forEach(item => {
          if (item.category_type === 'table') {
            // 查找关联的表格标题
            const tableCaption = pageItems.find(
              captionItem => captionItem.category_type === 'table_caption' && 
              captionItem.ref_id === item.id
            );
            
            tables.push({
              content: formatTableData(item),
              caption: tableCaption ? tableCaption.text : '',
              page: pageIndex + 1
            });
          }
        });
      });
      return tables;
    });
    
    const hasTables = computed(() => extractedTables.value.length > 0);

    const zoomIn = () => {
      scale.value = Math.min(scale.value + 0.1, 3);
    };

    const zoomOut = () => {
      scale.value = Math.max(scale.value - 0.1, 0.5);
    };

    const rotateLeft = () => {
      rotation.value = (rotation.value - 90) % 360;
    };

    const rotateRight = () => {
      rotation.value = (rotation.value + 90) % 360;
    };

    const resetImage = () => {
      scale.value = 1;
      rotation.value = 0;
      translateX.value = 0;
      translateY.value = 0;
    };

    const handleWheel = (e) => {
      if (e.deltaY < 0) {
        zoomIn();
      } else {
        zoomOut();
      }
    };

    const startDrag = (e) => {
      if (isEditingBox.value) return; // 如果正在编辑检测框，禁用拖动
      isDragging.value = true;
      startX.value = e.clientX - translateX.value;
      startY.value = e.clientY - translateY.value;
    };

    const onDrag = (e) => {
      if (!isDragging.value || isEditingBox.value) return; // 如果正在编辑检测框，禁用拖动
      translateX.value = e.clientX - startX.value;
      translateY.value = e.clientY - startY.value;
    };

    const stopDrag = () => {
      isDragging.value = false;
    };

    // 处理右侧标签点击事件
    const handleLabelClick = (index) => {
      if (selectedTab.value !== 'detection_results') return;
      
      selectedBoxIndex.value = index;
      isEditingBox.value = isEditMode.value; // 只有在编辑模式下才能编辑检测框
      editingPoint.value = -1;
      
      drawDetectionBoxes();
    };

    // 切换编辑模式
    const toggleEditMode = async () => {
      // 如果已经进行了修改，需要先保存或取消
      if (hasUnsavedChanges.value && !isEditMode.value) {
        if (!confirm('您有未保存的修改，确定要切换到编辑模式吗？修改将会丢失。')) {
          return;
        }
        resetChanges();
      }
      
      if (isEditMode.value) {
        // 保存模式
        try {
          let updatedResults;
          
          if (isImageFile.value) {
            // 处理图像文件编辑结果
            updatedResults = {
              detection_results: processingResult.value.detection_results.map((result, index) => ({
                ...result,
                label: editedLabels.value.get(index) || result.label
              })),
              predicted_label: editedPredictedLabel.value || processingResult.value.predicted_label
            };
          } else if (isPdfFile.value) {
            // 处理PDF文件编辑结果
            updatedResults = {
              layout_dets: processingResult.value.layout_dets
            };
          }

          // 发送更新请求，确保URL中的中文字符被正确编码
          const encodedProjectName = encodeURIComponent(projectName);
          const encodedFilename = encodeURIComponent(filename);
          
          let apiEndpoint = '';
          
          if (isImageFile.value) {
            apiEndpoint = `http://127.0.0.1:8000/api/update_image_detection_results/${encodedProjectName}/${encodedFilename}/`;
          } else if (isPdfFile.value) {
            // 使用正确的API路径
            apiEndpoint = `http://127.0.0.1:8000/api/update_pdf_results/${encodedProjectName}/${encodedFilename}/`;
          }
          
          await axios.post(apiEndpoint, updatedResults);

          // 重置本地更改状态
          resetChanges();
        } catch (error) {
          console.error('保存结果失败:', error);
          alert('保存失败，请重试');
          return;
        }
      }
      
      isEditMode.value = !isEditMode.value;
    };
    
    // 重置所有更改
    const resetChanges = () => {
      editedLabels.value.clear();
      editedPredictedLabel.value = '';
      hasUnsavedChanges.value = false;
    };
    
    // 处理图片标签编辑
    const handlePredictedLabelEdit = (event) => {
      if (!isEditMode.value) return;
      editedPredictedLabel.value = event.target.value;
      hasUnsavedChanges.value = true;
    };

    // 处理标签编辑
    const handleLabelEdit = (index, event) => {
      if (!isEditMode.value) return;
      
      // 如果标签内容被完全删除，提示用户是否删除该检测结果
      if (event.target.value.trim() === '') {
        if (confirm('您正在删除该标签，这将同时删除该目标检测结果。是否确认删除？')) {
          // 从检测结果中删除该项
          processingResult.value.detection_results.splice(index, 1);
          // 更新颜色映射
          boxColors.value.splice(index, 1);
          // 清除选中状态
          selectedBoxIndex.value = -1;
          // 标记有未保存的更改
          hasUnsavedChanges.value = true;
          // 重新绘制检测框
          nextTick(() => {
            drawDetectionBoxes();
          });
        } else {
          // 用户取消删除，恢复原值
          event.target.value = processingResult.value.detection_results[index].label;
        }
      } else {
        // 正常编辑标签
        editedLabels.value.set(index, event.target.value);
        hasUnsavedChanges.value = true;
      }
    };
    
    // 修改 watch 来监视编辑模式退出
    watch(isEditMode, (newValue, oldValue) => {
      if (!newValue && oldValue && hasUnsavedChanges.value) {
        if (confirm('您有未保存的更改，是否保存？')) {
          toggleEditMode();
        } else {
          resetChanges();
        }
      }
    });

    // 添加beforeUnmount钩子来处理页面离开前的提示
    onBeforeUnmount(() => {
      if (hasUnsavedChanges.value) {
        const result = confirm('您有未保存的更改，离开页面将丢失这些更改。是否保存？');
        if (result) {
          toggleEditMode();
        }
      }
    });

    // 处理布局文本编辑
    const handleLayoutTextEdit = () => {
      if (!isEditMode.value) return;
      
      // 直接使用processingResult的引用，所以不需要额外操作item.text
      // 标记有未保存的更改
      hasUnsavedChanges.value = true;
    };
    
    // 处理表格单元格编辑
    const handleTableCellEdit = (pageIndex, itemIndex, rowIndex, cellIndex, event) => {
      if (!isEditMode.value) return;
      
      // 更新结构化表格数据
      if (!processingResult.value.layout_dets[pageIndex][itemIndex].structured_content) {
        processingResult.value.layout_dets[pageIndex][itemIndex].structured_content = formatTableData(processingResult.value.layout_dets[pageIndex][itemIndex]);
      }
      
      processingResult.value.layout_dets[pageIndex][itemIndex].structured_content[rowIndex][cellIndex] = event.target.value;
      
      // 标记有未保存的更改
      hasUnsavedChanges.value = true;
    };

    // 处理布局类型改变
    const handleLayoutTypeChange = () => {
      if (!isEditMode.value) return;
      
      // 标记有未保存的更改
      hasUnsavedChanges.value = true;
    };

    // 提取图片和公式的计算属性
    const extractedFigures = computed(() => {
      if (!processingResult.value || !processingResult.value.layout_dets) return [];
      
      const figures = [];
      processingResult.value.layout_dets.forEach((pageItems, pageIndex) => {
        pageItems.forEach(item => {
          if (item.category_type === 'figure') {
            figures.push({
              image_url: item.image_url,
              caption: item.caption,
              page: pageIndex + 1
            });
          }
        });
      });
      return figures;
    });

    const extractedFormulas = computed(() => {
      if (!processingResult.value || !processingResult.value.layout_dets) return [];
      
      const formulas = [];
      processingResult.value.layout_dets.forEach((pageItems, pageIndex) => {
        pageItems.forEach(item => {
          if (item.category_type === 'isolated_formula') {
            formulas.push({
              latex: item.text,
              caption: item.caption,
              page: pageIndex + 1
            });
          }
        });
      });
      return formulas;
    });

    const hasFigures = computed(() => extractedFigures.value.length > 0);
    const hasFormulas = computed(() => extractedFormulas.value.length > 0);

    // 渲染LaTeX公式
    const renderLatex = (latex) => {
      try {
        return katex.renderToString(latex, {
          throwOnError: false,
          displayMode: true
        });
      } catch (error) {
        console.error('LaTeX渲染错误:', error);
        return latex;
      }
    };

    onMounted(() => {
      const fileExtension = filename.split('.').pop().toLowerCase();
      isTextFile.value = ['.txt', '.csv'].includes(`.${fileExtension}`);
      isImageFile.value = ['.jpg', '.jpeg', '.png'].includes(`.${fileExtension}`);
      isAudioFile.value = ['.wav', '.mp3'].includes(`.${fileExtension}`);
      isVideoFile.value = ['.aac', '.mp4'].includes(`.${fileExtension}`);
      isPdfFile.value = ['.pdf'].includes(`.${fileExtension}`);

      axios.get(`http://127.0.0.1:8000/api/get_file_content/${projectName}/${filename}/`, { responseType: 'blob' })
        .then((response) => {
          const url = URL.createObjectURL(response.data);
          previewUrl.value = url;

          if (isTextFile.value) {
            const reader = new FileReader();
            reader.onload = () => {
              textContent.value = reader.result;
            };
            reader.readAsText(response.data);
          } else if (isImageFile.value) {
            imgs.value = [{
              src: url,
              title: filename
            }];
          }
        })
        .catch((error) => {
          console.error('获取文件内容失败:', error);
        });

      axios.get(`http://127.0.0.1:8000/api/get_project_files/${projectName}/`)
        .then((response) => {
          projectFiles.value = response.data.files;
        })
        .catch((error) => {
          console.error('获取项目文件列表失败:', error);
        });

      axios.get(`http://127.0.0.1:8000/api/get_file_processing_result/${projectName}/${filename}/`)
        .then((response) => {
          processingResult.value = response.data;
          // 默认选中第一个结果
          if (isPdfFile.value) {
            selectedTab.value = 'layout_dets';
          } else if (isImageFile.value) {
            selectedTab.value = 'predicted_label';
          } else if (isAudioFile.value) {
            selectedTab.value = 'transcription';
          } else if (isVideoFile.value) {
            selectedTab.value = 'action_result';
          }
        })
        .catch((error) => {
          console.error('获取文件处理结果失败:', error);
        });
    });

    return {
      projectName,
      filename,
      prevFile,
      nextFile,
      isFirstFile,
      isLastFile,
      previewUrl,
      textContent,
      isTextFile,
      isImageFile,
      isAudioFile,
      isVideoFile,
      isPdfFile,
      projectFiles,
      viewFileDetails,
      processingResult,
      selectedTab,
      currentPdfPage,
      currentPageLayoutDets,
      visible,
      index,
      imgs,
      scale,
      rotation,
      isDragging,
      translateX,
      translateY,
      zoomIn,
      zoomOut,
      rotateLeft,
      rotateRight,
      resetImage,
      handleWheel,
      startDrag,
      onDrag,
      stopDrag,
      imageRef,
      onImageLoad,
      boxColors,
      handleLabelClick,
      isEditMode,
      toggleEditMode,
      editedLabels,
      handleLabelEdit,
      editedPredictedLabel,
      handlePredictedLabelEdit,
      hasUnsavedChanges,
      resetChanges,
      navigateToPrevFile,
      navigateToNextFile,
      selectedBoxIndex,
      getTypeDisplayName,
      formatTableData,
      getFigureAspectRatio,
      handleLayoutTextEdit,
      handleTableCellEdit,
      layoutTypeOptions,
      handleLayoutTypeChange,
      extractedFigures,
      extractedFormulas,
      hasFigures,
      hasFormulas,
      renderLatex,
      prevPage,
      nextPage,
      filteredCurrentPageLayoutItems,
      extractedTables,
      hasTables
    };
  }
};
</script>

<style scoped>
.file-detail-container {
  padding: 0px;
}

/* 路径顶部栏样式 */
.file-detail-top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f8f9fa;
  padding: 10px 20px;
  border-bottom: 1px solid #dee2e6;
  height: 8%;
}

/* 路径栏样式 */
.path-bar {
  font-size: 14px;
  color: #666;
}

.path-bar a {
  color: #007bff;
  text-decoration: none;
}

.path-bar a:hover {
  text-decoration: underline;
}

/* 导航按钮样式 */
.navigation-buttons {
  display: flex;
}

.action-button {
  padding: 5px 10px;
  margin-left: 10px;
  border: none;
  background-color: #007bff;
  color: white;
  border-radius: 3px;
  cursor: pointer;
}

.action-button:hover {
  background-color: #0056b3;
}

/* 路径栏分隔线 */
.path-bar-divider {
  border-bottom: 1px solid #ccc;
  margin-bottom: 0px;
  width: 100%;
}

/* 灰线以下内容容器 */
.content-container {
  display: flex;
  position: relative;
  height: calc(100vh - 100px); /* 减去顶部栏的高度 */
  padding-bottom: 0px; /* 为底部栏留出空间 */
}

/* 左侧文件列表样式 */
.file-list-container {
  width: 15%;
  border-right: 1px solid #ccc;
  padding: 0px;
  height: 100%;
  overflow-y: auto;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}

.file-list-container::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}

.file-list {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.file-item {
  cursor: pointer;
  padding: 5px;
  word-wrap: break-word;
  word-break: break-all;
  white-space: normal;
}

.file-item:hover {
  background-color: #f0f0f0;
}

/* 中间文件预览区域样式 */
.file-preview-container {
  width: 60%;
  position: relative;
  padding: 0px;
  height: 100%;
}

.centered-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

/* 右侧解析结果区域样式 */
.analysis-result-container {
  height: 100%;
  width: 25%;
  overflow-y: auto;
  position: relative;
}

/* 解析结果内容样式 */
.result-content {
  padding: 5px;
  white-space: pre-wrap; /* 保留空白字符并换行 */
  word-break: break-word; /* 当内容超出容器宽度时，单词会被强制拆分换行 */
}

/* 分隔线样式 */
.divider {
  border-right: 1px solid #ccc;
}

/* 右侧解析区域顶部栏样式 */
.result-top-bar.fixed-top {
  height: 7%;
  display: flex;
  align-items: center;
  border-bottom: 1px solid #ccc;
  padding: 0 10px;
  position: sticky;
  top: 0;
  background-color: white;
  z-index: 1;
}

.result-top-bar button {
  padding: 5px 10px;
  margin-right: 10px;
  border: none;
  background-color: transparent;
  color: blue;
  cursor: pointer;
}

.result-top-bar button:hover {
  text-decoration: underline;
}

.image-preview-container {
  width: 100%;
  height: 600px;
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: #f5f5f5;
  position: relative;
}

.image-controls {
  padding: 10px;
  display: flex;
  gap: 10px;
  justify-content: center;
  width: 100%;
  position: absolute;
  top: 0;
  left: 0;
  z-index: 1;
}

.control-button {
  padding: 5px 10px;
  border: 1px solid #ddd;
  background-color: #fff;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.control-button:hover {
  background-color: #f0f0f0;
  border-color: #999;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.image-wrapper {
  width: 100%;
  height: 100%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  margin-top: 50px;
}

.detection-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: auto;
  z-index: 10;
}

.image-wrapper img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  transition: transform 0.1s ease;
  user-select: none;
  will-change: transform;
}

.detection-results {
  padding: 10px;
}

.detection-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  margin-bottom: 8px;
  background-color: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #dee2e6;
  transition: border-color 0.3s, background-color 0.3s;
  cursor: pointer;
}

.detection-item:hover {
  background-color: #e9ecef;
}

.selected-item {
  background-color: #e9ecef;
  border-width: 2px !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
  transition: all 0.2s ease;
}

.detection-item:not(.selected-item):hover {
  background-color: #f8f9fa;
  transform: translateY(-1px);
  transition: all 0.2s ease;
}

.detection-item .label {
  font-weight: 500;
  color: #333;
  transition: color 0.3s;
}

.detection-item .confidence {
  color: #666;
  font-family: monospace;
}

.layout-results {
  padding: 10px;
}

.layout-item {
  margin-bottom: 15px;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #dee2e6;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  transition: all 0.2s ease;
}

.layout-item:hover {
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
  transform: translateY(-1px);
}

/* 根据类型定义不同的边框颜色 */
.layout-item.plain_text, .layout-item.text {
  border-left-color: #28a745; /* 绿色 */
}

.layout-item.title {
  border-left-color: #007bff; /* 蓝色 */
}

.layout-item.table {
  border-left-color: #6f42c1; /* 紫色 */
}

.layout-item.figure {
  border-left-color: #fd7e14; /* 橙色 */
}

.layout-item.list {
  border-left-color: #17a2b8; /* 青色 */
}

.layout-item.formula {
  border-left-color: #dc3545; /* 红色 */
}

.layout-item.header, .layout-item.footer {
  border-left-color: #6c757d; /* 灰色 */
  background-color: #f2f2f2;
}

.layout-item.footnote, .layout-item.caption, .layout-item.figure_caption, .layout-item.table_caption, .layout-item.formula_caption, .layout-item.table_footnote {
  border-left-color: #20c997; /* 青绿色 */
  font-size: 0.9em;
}

.layout-item.abandoned_text {
  border-left-color: #adb5bd; /* 浅灰色 */
  font-style: italic;
}

.layout-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding-bottom: 5px;
  border-bottom: 1px solid #eee;
}

.layout-type {
  font-weight: 600;
  font-size: 0.9em;
  text-transform: uppercase;
  background-color: #f0f0f0;
  padding: 3px 8px;
  border-radius: 4px;
}

.layout-confidence {
  color: #666;
  font-size: 0.8em;
  font-family: monospace;
  background-color: #f0f0f0;
  padding: 2px 6px;
  border-radius: 4px;
}

.layout-content {
  margin-top: 8px;
}

.layout-content p {
  margin: 0;
  line-height: 1.5;
}

/* 表格样式优化 */
.table-preview {
  margin-top: 10px;
  max-height: 300px;
  overflow-x: auto;
  overflow-y: auto;
  border-radius: 4px;
  border: 1px solid #dee2e6;
}

.table-preview table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9em;
}

.table-preview table tr:nth-child(even) {
  background-color: #f2f2f2;
}

.table-preview table tr:hover {
  background-color: #e9ecef;
}

.table-preview table td {
  padding: 8px;
  border: 1px solid #dee2e6;
  word-break: break-word;
}

/* 图片预览区样式 */
.figure-preview {
  margin-top: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f5f5;
  border-radius: 4px;
  border: 1px solid #dee2e6;
  padding: 10px;
}

.figure-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  background: repeating-linear-gradient(
    45deg,
    #f5f5f5,
    #f5f5f5 10px,
    #eeeeee 10px,
    #eeeeee 20px
  );
  border-radius: 4px;
  color: #666;
  font-weight: 500;
}

.figure-placeholder span {
  background-color: rgba(255,255,255,0.7);
  padding: 5px 10px;
  border-radius: 4px;
}

.content-text {
  margin: 0;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.content-title {
  margin: 0;
  font-size: 1.5em;
  font-weight: 600;
  margin-bottom: 10px;
}

.content-formula {
  margin-top: 10px;
  margin-bottom: 10px;
}

.formula-box {
  background-color: #f0f0f0;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #dee2e6;
}

.content-list {
  margin-top: 10px;
  margin-left: 20px;
}

.content-list ul {
  list-style-type: disc;
}

.page-divider {
  text-align: center;
  font-weight: bold;
  color: #989898;
  padding: 5px;
}

.page-info {
  padding: 10px;
}

.page-info-content {
  margin: 10px 0;
}

.info-item {
  margin: 5px 0;
  display: flex;
  align-items: center;
}

.info-label {
  font-weight: 500;
  margin-right: 10px;
  color: #666;
}

.info-value {
  color: #333;
}

.no-data-message {
  text-align: center;
  color: #666;
}

/* 编辑模式下的输入框样式 */
.content-text-edit, .content-formula-edit, .content-list-edit {
  width: 100%;
  min-height: 100px;
  padding: 8px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-family: inherit;
  font-size: inherit;
  line-height: 1.5;
  resize: vertical;
}

.content-title-edit {
  width: 100%;
  padding: 8px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-family: inherit;
  font-size: 1.5em;
  font-weight: 600;
  line-height: 1.5;
}

.table-cell-edit {
  width: 100%;
  padding: 4px;
  border: 1px solid #ced4da;
  border-radius: 2px;
  font-family: inherit;
  font-size: inherit;
}

.layout-type-select {
  padding: 5px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  background-color: #fff;
  font-weight: 600;
  font-size: 0.9em;
}

/* 保存按钮样式 */
.save-button {
  background-color: #28a745 !important;
}

.save-button:hover {
  background-color: #218838 !important;
}

/* 图片展示区域样式 */
.figures-container {
  padding: 15px;
}

.figures-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  padding: 10px;
}

.figure-item {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
  transition: transform 0.2s;
}

.figure-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.figure-preview {
  width: 100%;
  aspect-ratio: 1;
  overflow: hidden;
  background: #f5f5f5;
}

.figure-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.figure-caption {
  padding: 10px;
  font-size: 0.9em;
  color: #666;
  background: #f8f9fa;
  border-top: 1px solid #eee;
}

/* 公式展示区域样式 */
.formulas-container {
  padding: 15px;
}

.formulas-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.formula-item {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 15px;
  transition: transform 0.2s;
}

.formula-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.formula-latex {
  display: flex;
  justify-content: center;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  width: 100%;
  min-width: 0;
}

.latex-render {
  font-size: 0.9em;
  transform: scale(0.9);
  transform-origin: center;
  min-width: min-content;
  padding: 0 10px;
}

.formula-caption {
  margin-top: 10px;
  font-size: 0.9em;
  color: #666;
  text-align: center;
}

.page-selector {
  display: flex;
  align-items: center;
  position: fixed;
  bottom: 10px;
  left: auto;
  right: 5%;
  background-color: white;
  padding: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.page-button {
  padding: 5px 10px;
  margin: 0 5px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  cursor: pointer;
  background-color: #f8f9fa;
}

.page-select {
  padding: 5px;
  border: 1px solid #ced4da;
  border-radius: 4px;
}

.page-count {
  margin: 0 10px;
}

.tables-container {
  padding: 15px;
}

.tables-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.table-item {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 15px;
  transition: transform 0.2s;
}

.table-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.table-label {
  font-weight: 600;
}

.table-page {
  color: #666;
  font-size: 0.9em;
}

.table-content {
  margin-top: 10px;
  overflow-x: auto;
  border: 1px solid #dee2e6;
  border-radius: 4px;
}

.table-content table {
  width: 100%;
  border-collapse: collapse;
}

.table-content table tr:nth-child(even) {
  background-color: #f8f9fa;
}

.table-content table tr:hover {
  background-color: #e9ecef;
}

.table-content table td {
  padding: 8px 12px;
  border: 1px solid #dee2e6;
  text-align: left;
}

.table-content table tr:first-child td {
  background-color: #f1f1f1;
  font-weight: 500;
  border-bottom: 2px solid #dee2e6;
}

.table-caption {
  margin-top: 10px;
  font-size: 0.9em;
  color: #666;
  text-align: center;
  font-style: italic;
}
</style>