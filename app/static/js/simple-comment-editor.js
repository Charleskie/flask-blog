/**
 * 简化版评论编辑器
 * 只支持表情包和图片功能
 */

class SimpleCommentEditor {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            placeholder: '发表你的评论...',
            content: '',
            ...options
        };
        this.editor = null;
        this.toolbar = null;
        this.content = null;
        this.emojiPicker = null;
        
        // 将编辑器实例存储到容器元素上，方便外部访问
        container.simpleCommentEditor = this;
        this.init();
    }

    init() {
        this.createEditor();
        this.bindEvents();
        this.createEmojiPicker();
    }

    createEditor() {
        // 创建编辑器HTML结构
        this.container.innerHTML = `
            <div class="simple-comment-editor">
                <div class="comment-toolbar">
                    <div class="toolbar-group">
                        <button class="toolbar-btn emoji-btn" title="表情包">
                            <i class="fas fa-smile"></i>
                        </button>
                        <button class="toolbar-btn image-btn" title="插入图片">
                            <i class="fas fa-image"></i>
                        </button>
                    </div>
                </div>
                
                <div class="comment-content" data-placeholder="${this.options.placeholder}" contenteditable="true"></div>
            </div>
        `;

        this.toolbar = this.container.querySelector('.comment-toolbar');
        this.content = this.container.querySelector('.comment-content');
        
        // 设置初始内容
        if (this.options.content) {
            this.content.innerHTML = this.options.content;
        }
        
        // 更新占位符状态
        this.updatePlaceholder();
    }

    createEmojiPicker() {
        // 创建表情选择器
        const emojiBtn = this.toolbar.querySelector('.emoji-btn');
        const emojiPicker = document.createElement('div');
        emojiPicker.className = 'emoji-picker';
        
        // 常用表情包（64个精选）
        const emojis = [
            '😀', '😃', '😄', '😁', '😆', '😅', '🤣', '😂', '🙂', '🙃', '😉', '😊', '😇', '🥰', '😍', '🤩',
            '😘', '😗', '😚', '😙', '😋', '😛', '😜', '🤪', '😝', '🤑', '🤗', '🤭', '🤫', '🤔', '🤐', '🤨',
            '😐', '😑', '😶', '😏', '😒', '🙄', '😬', '🤥', '😔', '😪', '🤤', '😴', '😷', '🤒', '🤕', '🤢',
            '🤮', '🤧', '🥵', '🥶', '🥴', '😵', '🤯', '🤠', '🥳', '😎', '🤓', '🧐', '😕', '😟', '🙁', '☹️',
            '👍', '👎', '👌', '✌️', '🤞', '🤟', '🤘', '🤙', '👈', '👉', '👆', '👇', '☝️', '✋', '🤚', '🖐️',
            '🖖', '👋', '🤝', '👏', '🙌', '👐', '🤲', '🤜', '🤛', '✊', '👊', '👎', '👌', '✌️', '🤞', '🤟'
        ];

        // 创建表情网格
        const emojiGrid = document.createElement('div');
        emojiGrid.className = 'emoji-grid';
        
        emojis.forEach(emoji => {
            const emojiItem = document.createElement('div');
            emojiItem.className = 'emoji-item';
            emojiItem.textContent = emoji;
            emojiItem.addEventListener('click', () => {
                this.insertEmoji(emoji);
                emojiPicker.classList.remove('show');
            });
            emojiGrid.appendChild(emojiItem);
        });

        emojiPicker.appendChild(emojiGrid);
        
        // 将表情选择器添加到表情按钮的父节点，并设置相对定位
        emojiBtn.parentNode.style.position = 'relative';
        emojiBtn.parentNode.appendChild(emojiPicker);
        this.emojiPicker = emojiPicker;
        this.emojiBtn = emojiBtn;
    }

    bindEvents() {
        // 工具栏按钮事件
        this.toolbar.addEventListener('click', (e) => {
            const button = e.target.closest('.toolbar-btn');
            if (button) {
                e.preventDefault();
                if (button.classList.contains('emoji-btn')) {
                    this.toggleEmojiPicker();
                } else if (button.classList.contains('image-btn')) {
                    this.setImage();
                }
            }
        });

        // 编辑器内容变化事件
        this.content.addEventListener('input', () => {
            this.updatePlaceholder();
            if (this.onContentChange) {
                this.onContentChange(this.getContent());
            }
        });

        // 编辑器焦点事件
        this.content.addEventListener('focus', () => {
            this.updatePlaceholder();
        });

        // 点击外部关闭表情选择器
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.emoji-picker') && !e.target.closest('.emoji-btn')) {
                this.emojiPicker.classList.remove('show');
            }
        });

        // 粘贴事件处理
        this.content.addEventListener('paste', (e) => {
            e.preventDefault();
            const text = (e.clipboardData || window.clipboardData).getData('text/plain');
            document.execCommand('insertText', false, text);
        });
    }

    insertEmoji(emoji) {
        this.content.focus();
        document.execCommand('insertText', false, emoji);
    }

    setImage() {
        this.showImageModal();
    }

    showImageModal() {
        // 创建图片选择模态框
        const modal = document.createElement('div');
        modal.className = 'image-modal';
        modal.innerHTML = `
            <div class="image-modal-overlay">
                <div class="image-modal-content">
                    <div class="image-modal-header">
                        <h3>插入图片</h3>
                        <button class="image-modal-close">&times;</button>
                    </div>
                    <div class="image-modal-body">
                        <div class="image-tabs">
                            <button class="image-tab active" data-tab="url">图片链接</button>
                            <button class="image-tab" data-tab="upload">上传图片</button>
                        </div>
                        
                        <div class="image-tab-content active" id="url-tab">
                            <div class="form-group">
                                <label for="image-url">图片地址</label>
                                <input type="url" id="image-url" placeholder="https://example.com/image.jpg" class="form-control">
                            </div>
                            <div class="form-group">
                                <label for="image-alt">图片描述（可选）</label>
                                <input type="text" id="image-alt" placeholder="图片描述" class="form-control">
                            </div>
                        </div>
                        
                        <div class="image-tab-content" id="upload-tab">
                            <div class="upload-area" id="upload-area">
                                <div class="upload-icon">
                                    <i class="fas fa-cloud-upload-alt"></i>
                                </div>
                                <p>点击选择图片或拖拽图片到此处</p>
                                <p class="upload-hint">支持 JPG、PNG、GIF、WebP 格式，最大 5MB</p>
                                <input type="file" id="image-file" accept="image/*" style="display: none;">
                            </div>
                            <div class="upload-preview" id="upload-preview" style="display: none;">
                                <img id="preview-img" src="" alt="预览">
                                <div class="preview-info">
                                    <p id="preview-name"></p>
                                    <p id="preview-size"></p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="image-modal-footer">
                        <button class="btn btn-secondary" id="cancel-image">取消</button>
                        <button class="btn btn-primary" id="insert-image" disabled>插入图片</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // 绑定事件
        this.bindImageModalEvents(modal);
    }

    bindImageModalEvents(modal) {
        const closeBtn = modal.querySelector('.image-modal-close');
        const cancelBtn = modal.querySelector('#cancel-image');
        const insertBtn = modal.querySelector('#insert-image');
        const tabs = modal.querySelectorAll('.image-tab');
        const tabContents = modal.querySelectorAll('.image-tab-content');
        const urlInput = modal.querySelector('#image-url');
        const altInput = modal.querySelector('#image-alt');
        const uploadArea = modal.querySelector('#upload-area');
        const fileInput = modal.querySelector('#image-file');
        const uploadPreview = modal.querySelector('#upload-preview');
        const previewImg = modal.querySelector('#preview-img');
        const previewName = modal.querySelector('#preview-name');
        const previewSize = modal.querySelector('#preview-size');
        
        let selectedFile = null;
        let currentTab = 'url';
        
        // 关闭模态框
        const closeModal = () => {
            document.body.removeChild(modal);
        };
        
        closeBtn.addEventListener('click', closeModal);
        cancelBtn.addEventListener('click', closeModal);
        modal.querySelector('.image-modal-overlay').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) {
                closeModal();
            }
        });
        
        // 标签页切换
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const tabName = tab.dataset.tab;
                
                // 更新标签页状态
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                // 更新内容显示
                tabContents.forEach(content => {
                    content.classList.remove('active');
                });
                modal.querySelector(`#${tabName}-tab`).classList.add('active');
                
                currentTab = tabName;
                updateInsertButton();
            });
        });
        
        // URL输入变化
        urlInput.addEventListener('input', () => {
            updateInsertButton();
        });
        
        // 文件上传区域
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileSelect(files[0]);
            }
        });
        
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelect(e.target.files[0]);
            }
        });
        
        // 处理文件选择
        const handleFileSelect = (file) => {
            // 检查文件类型
            if (!file.type.startsWith('image/')) {
                alert('请选择图片文件');
                return;
            }
            
            // 检查文件大小 (5MB)
            if (file.size > 5 * 1024 * 1024) {
                alert('图片大小不能超过5MB');
                return;
            }
            
            selectedFile = file;
            
            // 显示预览
            const reader = new FileReader();
            reader.onload = (e) => {
                previewImg.src = e.target.result;
                previewName.textContent = file.name;
                previewSize.textContent = this.formatFileSize(file.size);
                uploadArea.style.display = 'none';
                uploadPreview.style.display = 'block';
            };
            reader.readAsDataURL(file);
            
            updateInsertButton();
        };
        
        // 更新插入按钮状态
        const updateInsertButton = () => {
            let canInsert = false;
            
            if (currentTab === 'url') {
                canInsert = urlInput.value.trim() !== '';
            } else if (currentTab === 'upload') {
                canInsert = selectedFile !== null;
            }
            
            insertBtn.disabled = !canInsert;
        };
        
        // 插入图片
        insertBtn.addEventListener('click', async () => {
            if (currentTab === 'url') {
                const url = urlInput.value.trim();
                const alt = altInput.value.trim();
                this.insertImage(url, alt);
                closeModal();
            } else if (currentTab === 'upload' && selectedFile) {
                insertBtn.disabled = true;
                insertBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 上传中...';
                
                try {
                    const imageUrl = await this.uploadImage(selectedFile);
                    if (imageUrl) {
                        this.insertImage(imageUrl, selectedFile.name);
                        closeModal();
                    } else {
                        alert('图片上传失败');
                    }
                } catch (error) {
                    console.error('上传错误:', error);
                    alert('图片上传失败');
                } finally {
                    insertBtn.disabled = false;
                    insertBtn.innerHTML = '插入图片';
                }
            }
        });
    }

    insertImage(url, alt = '') {
        this.content.focus();
        const img = document.createElement('img');
        img.src = url;
        img.alt = alt;
        img.style.maxWidth = '200px';
        img.style.maxHeight = '200px';
        img.style.height = 'auto';
        img.style.borderRadius = '6px';
        img.style.margin = '8px 0';
        img.style.display = 'block';
        img.style.transition = 'all 0.2s ease';
        img.style.objectFit = 'cover';
        
        // 插入图片
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            range.insertNode(img);
            // 移动光标到图片后面
            range.setStartAfter(img);
            range.setEndAfter(img);
            selection.removeAllRanges();
            selection.addRange(range);
        } else {
            this.content.appendChild(img);
        }
        
        // 在图片插入到DOM后添加调整大小功能
        this.makeImageResizable(img);
    }

    async uploadImage(file) {
        try {
            // 压缩图片
            const compressedFile = await this.compressImage(file);
            
            // 创建FormData对象
            const formData = new FormData();
            formData.append('image', compressedFile);
            
            // 发送到服务器上传
            const response = await fetch('/api/upload-image', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const result = await response.json();
                if (result.success) {
                    return result.url;
                } else {
                    throw new Error(result.message || '上传失败');
                }
            } else {
                // 尝试获取错误信息
                let errorMessage = '上传失败';
                try {
                    const errorResult = await response.json();
                    errorMessage = errorResult.message || errorMessage;
                } catch (e) {
                    errorMessage = `上传失败 (${response.status}: ${response.statusText})`;
                }
                throw new Error(errorMessage);
            }
        } catch (error) {
            console.error('图片上传错误:', error);
            throw error;
        }
    }

    async compressImage(file, maxWidth = 800, maxHeight = 600, quality = 0.8) {
        return new Promise((resolve) => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();
            
            img.onload = () => {
                // 计算压缩后的尺寸
                let { width, height } = img;
                
                if (width > maxWidth || height > maxHeight) {
                    const ratio = Math.min(maxWidth / width, maxHeight / height);
                    width *= ratio;
                    height *= ratio;
                }
                
                canvas.width = width;
                canvas.height = height;
                
                // 绘制压缩后的图片
                ctx.drawImage(img, 0, 0, width, height);
                
                // 转换为Blob
                canvas.toBlob((blob) => {
                    resolve(blob);
                }, file.type, quality);
            };
            
            img.src = URL.createObjectURL(file);
        });
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    toggleEmojiPicker() {
        const isShowing = this.emojiPicker.classList.contains('show');
        
        if (isShowing) {
            this.emojiPicker.classList.remove('show');
        } else {
            // 计算表情选择器的位置
            const btnRect = this.emojiBtn.getBoundingClientRect();
            const toolbarRect = this.toolbar.getBoundingClientRect();
            
            // 设置表情选择器的位置
            this.emojiPicker.style.left = '0px';
            this.emojiPicker.style.top = '100%';
            
            this.emojiPicker.classList.add('show');
        }
    }

    updatePlaceholder() {
        const isEmpty = this.content.innerHTML.trim() === '' || this.content.innerHTML.trim() === '<br>';
        this.content.classList.toggle('is-empty', isEmpty);
    }

    getContent() {
        return this.content.innerHTML;
    }

    setContent(content) {
        this.content.innerHTML = content;
        this.updatePlaceholder();
    }

    getTextContent() {
        return this.content.textContent || this.content.innerText || '';
    }

    clear() {
        this.content.innerHTML = '';
        this.updatePlaceholder();
    }

    focus() {
        this.content.focus();
    }

    makeImageResizable(img) {
        // 检查图片是否在DOM中
        if (!img.parentNode) {
            console.warn('图片尚未插入到DOM中，无法添加调整大小功能');
            return;
        }
        
        // 创建包装容器
        const wrapper = document.createElement('div');
        wrapper.className = 'comment-image-resize-wrapper';
        wrapper.style.position = 'relative';
        wrapper.style.display = 'inline-block';
        wrapper.style.maxWidth = '200px';
        wrapper.style.maxHeight = '200px';
        
        // 将图片包装在容器中
        img.parentNode.insertBefore(wrapper, img);
        wrapper.appendChild(img);
        
        // 添加resizable类到包装器
        wrapper.classList.add('resizable');
        
        // 创建调整大小控制点
        const handles = ['nw', 'ne', 'sw', 'se'];
        handles.forEach(handle => {
            const resizeHandle = document.createElement('div');
            resizeHandle.className = `resize-handle ${handle}`;
            wrapper.appendChild(resizeHandle);
            
            // 添加拖拽调整大小功能
            resizeHandle.addEventListener('mousedown', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                const startX = e.clientX;
                const startY = e.clientY;
                const startWidth = wrapper.offsetWidth;
                const startHeight = wrapper.offsetHeight;
                const startLeft = wrapper.offsetLeft;
                const startTop = wrapper.offsetTop;
                
                const handleMouseMove = (e) => {
                    const deltaX = e.clientX - startX;
                    const deltaY = e.clientY - startY;
                    
                    let newWidth = startWidth;
                    let newHeight = startHeight;
                    let newLeft = startLeft;
                    let newTop = startTop;
                    
                    // 根据控制点位置调整大小
                    if (handle.includes('e')) {
                        newWidth = Math.max(50, startWidth + deltaX);
                    }
                    if (handle.includes('w')) {
                        newWidth = Math.max(50, startWidth - deltaX);
                        newLeft = startLeft + deltaX;
                    }
                    if (handle.includes('s')) {
                        newHeight = Math.max(50, startHeight + deltaY);
                    }
                    if (handle.includes('n')) {
                        newHeight = Math.max(50, startHeight - deltaY);
                        newTop = startTop + deltaY;
                    }
                    
                    // 限制最大尺寸（评论图片最大200px）
                    newWidth = Math.min(newWidth, 200);
                    newHeight = Math.min(newHeight, 200);
                    
                    // 应用新尺寸到包装器
                    wrapper.style.width = newWidth + 'px';
                    wrapper.style.height = newHeight + 'px';
                    wrapper.style.left = newLeft + 'px';
                    wrapper.style.top = newTop + 'px';
                    wrapper.style.position = 'relative';
                    
                    // 图片填满包装器
                    img.style.width = '100%';
                    img.style.height = '100%';
                    img.style.objectFit = 'cover';
                };
                
                const handleMouseUp = () => {
                    document.removeEventListener('mousemove', handleMouseMove);
                    document.removeEventListener('mouseup', handleMouseUp);
                };
                
                document.addEventListener('mousemove', handleMouseMove);
                document.addEventListener('mouseup', handleMouseUp);
            });
        });
    }


    destroy() {
        // 清理事件监听器
        if (this.content) {
            this.content.removeEventListener('input', this.updatePlaceholder);
            this.content.removeEventListener('focus', this.updatePlaceholder);
        }
    }
}

// 导出类
window.SimpleCommentEditor = SimpleCommentEditor;
