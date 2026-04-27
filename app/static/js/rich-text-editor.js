/**
 * 富文本编辑器
 * 支持文字格式、字体、大小、表情包、图片输入
 */

class RichTextEditor {
    constructor(container) {
        this.container = container;
        this.editor = null;
        this.toolbar = null;
        this.content = null;
        this.emojiPicker = null;
        this.imageModal = null;
        // 将编辑器实例存储到容器元素上，方便外部访问
        container.richTextEditor = this;
        this.init();
    }

    init() {
        this.createEditor();
        this.bindEvents();
        this.createEmojiPicker();
        this.createImageModal();
    }

    createEditor() {
        // 创建编辑器HTML结构
        this.container.innerHTML = `
            <div class="rich-text-editor">
                <div class="editor-toolbar">
                    <!-- 文字格式 -->
                    <button class="toolbar-btn" data-command="bold" title="粗体">
                        <i class="fas fa-bold"></i>
                    </button>
                    <button class="toolbar-btn" data-command="italic" title="斜体">
                        <i class="fas fa-italic"></i>
                    </button>
                    <button class="toolbar-btn" data-command="underline" title="下划线">
                        <i class="fas fa-underline"></i>
                    </button>
                    <button class="toolbar-btn" data-command="strikeThrough" title="删除线">
                        <i class="fas fa-strikethrough"></i>
                    </button>
                    
                    <div class="toolbar-separator"></div>
                    
                    <!-- 字体选择 -->
                    <select class="toolbar-select" data-command="fontName">
                        <option value="">选择字体</option>
                        <option value="Arial">Arial</option>
                        <option value="Helvetica">Helvetica</option>
                        <option value="Times New Roman">Times New Roman</option>
                        <option value="Georgia">Georgia</option>
                        <option value="Verdana">Verdana</option>
                        <option value="Courier New">Courier New</option>
                        <option value="微软雅黑">微软雅黑</option>
                        <option value="宋体">宋体</option>
                        <option value="黑体">黑体</option>
                    </select>
                    
                    <!-- 字体大小 -->
                    <select class="toolbar-select" data-command="fontSize">
                        <option value="">字体大小</option>
                        <option value="1">1</option>
                        <option value="2">2</option>
                        <option value="3">3</option>
                        <option value="4">4</option>
                        <option value="5">5</option>
                        <option value="6">6</option>
                        <option value="7">7</option>
                    </select>
                    
                    <div class="toolbar-separator"></div>
                    
                    <!-- 文字颜色 -->
                    <div class="color-picker-wrapper" style="position: relative; display: inline-block;">
                        <button class="toolbar-btn" id="color-picker-trigger" title="文字颜色">
                            <i class="fas fa-palette"></i>
                        </button>
                        <input type="color" id="color-picker-input" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; opacity: 0; cursor: pointer; border: none; padding: 0; margin: 0;">
                    </div>
                    
                    <div class="toolbar-separator"></div>
                    
                    <!-- 对齐方式 -->
                    <button class="toolbar-btn" data-command="justifyLeft" title="左对齐">
                        <i class="fas fa-align-left"></i>
                    </button>
                    <button class="toolbar-btn" data-command="justifyCenter" title="居中">
                        <i class="fas fa-align-center"></i>
                    </button>
                    <button class="toolbar-btn" data-command="justifyRight" title="右对齐">
                        <i class="fas fa-align-right"></i>
                    </button>
                    
                    <div class="toolbar-separator"></div>
                    
                    <!-- 列表 -->
                    <button class="toolbar-btn" data-command="insertUnorderedList" title="无序列表">
                        <i class="fas fa-list-ul"></i>
                    </button>
                    <button class="toolbar-btn" data-command="insertOrderedList" title="有序列表">
                        <i class="fas fa-list-ol"></i>
                    </button>
                    
                    <div class="toolbar-separator"></div>
                    
                    <!-- 表情包 -->
                    <button class="toolbar-btn emoji-btn" title="表情包">
                        <i class="fas fa-smile"></i>
                    </button>
                    
                    <!-- 图片 -->
                    <button class="toolbar-btn image-btn" title="插入图片">
                        <i class="fas fa-image"></i>
                    </button>
                    
                    <div class="toolbar-separator"></div>
                    
                    <!-- 清除格式 -->
                    <button class="toolbar-btn" data-command="removeFormat" title="清除格式">
                        <i class="fas fa-remove-format"></i>
                    </button>
                </div>
                <div class="editor-content" contenteditable="true" data-placeholder="分享你的想法..."></div>
            </div>
        `;

        this.editor = this.container.querySelector('.rich-text-editor');
        this.toolbar = this.container.querySelector('.editor-toolbar');
        this.content = this.container.querySelector('.editor-content');
    }

    createEmojiPicker() {
        // 创建表情选择器
        const emojiBtn = this.toolbar.querySelector('.emoji-btn');
        const emojiPicker = document.createElement('div');
        emojiPicker.className = 'emoji-picker';
        
        // 常用表情包（256个）
        const emojis = [
            '😀', '😃', '😄', '😁', '😆', '😅', '🤣', '😂', '🙂', '🙃', '😉', '😊', '😇', '🥰', '😍', '🤩',
            '😘', '😗', '😚', '😙', '😋', '😛', '😜', '🤪', '😝', '🤑', '🤗', '🤭', '🤫', '🤔', '🤐', '🤨',
            '😐', '😑', '😶', '😏', '😒', '🙄', '😬', '🤥', '😔', '😪', '🤤', '😴', '😷', '🤒', '🤕', '🤢',
            '🤮', '🤧', '🥵', '🥶', '🥴', '😵', '🤯', '🤠', '🥳', '😎', '🤓', '🧐', '😕', '😟', '🙁', '☹️',
            '😮', '😯', '😲', '😳', '🥺', '😦', '😧', '😨', '😰', '😥', '😢', '😭', '😱', '😖', '😣', '😞',
            '😓', '😩', '😫', '🥱', '😤', '😡', '😠', '🤬', '😈', '👿', '💀', '☠️', '💩', '🤡', '👹', '👺',
            '👻', '👽', '👾', '🤖', '😺', '😸', '😹', '😻', '😼', '😽', '🙀', '😿', '😾', '👶', '🧒', '👦',
            '👧', '🧑', '👨', '👩', '🧓', '👴', '👵', '👱', '👱‍♀️', '👱‍♂️', '🧔', '👨‍🦰', '👩‍🦰', '👨‍🦱', '👩‍🦱', '👨‍🦳',
            '👩‍🦳', '👨‍🦲', '👩‍🦲', '🤵', '👰', '🤰', '🤱', '👼', '🎅', '🤶', '🦸', '🦹', '🧙', '🧚', '🧛', '🧜', '🧝',
            '🧞', '🧟', '💆', '💇', '🚶', '🏃', '💃', '🕺', '👯', '🧖', '🧗', '🤺', '🏇', '⛷️', '🏂', '🏌️',
            '🏄', '🚣', '🏊', '⛹️', '🏋️', '🚴', '🚵', '🤸', '🤼', '🤽', '🤾', '🤹', '🧘', '🛀', '🛌', '👭',
            '👫', '👬', '💏', '💑', '👪', '🗣️', '👤', '👥', '👣', '🐵', '🐒', '🦍', '🦧', '🐶', '🐕', '🦮',
            '🐕‍🦺', '🐩', '🐺', '🦊', '🦝', '🐱', '🐈', '🦁', '🐯', '🐅', '🐆', '🐴', '🐎', '🦄', '🦓', '🦌',
            '🐮', '🐂', '🐃', '🐄', '🐷', '🐖', '🐗', '🐽', '🐏', '🐑', '🐐', '🐪', '🐫', '🦙', '🦒', '🐘',
            '🦏', '🦛', '🐭', '🐁', '🐀', '🐹', '🐰', '🐇', '🐿️', '🦔', '🦇', '🐻', '🐨', '🐼', '🦥', '🦦',
            '🦨', '🦘', '🦡', '🐾', '🦃', '🐔', '🐓', '🐣', '🐤', '🐥', '🐦', '🦅', '🦆', '🦢', '🦉', '🦩',
            '🦚', '🦜', '🐸', '🐊', '🐢', '🦎', '🐍', '🐲', '🐉', '🦕', '🦖', '🐳', '🐋', '🐬', '🦭', '🐟',
            '🐠', '🐡', '🦈', '🐙', '🐚', '🐌', '🦋', '🐛', '🐜', '🐝', '🐞', '🦗', '🕷️', '🕸️', '🦂', '🦟',
            '🦠', '💐', '🌸', '💮', '🏵️', '🌹', '🥀', '🌺', '🌻', '🌼', '🌷', '🌱', '🌲', '🌳', '🌴', '🌵',
            '🌶️', '🌽', '🌾', '🌿', '🍀', '🍁', '🍂', '🍃', '🍇', '🍈', '🍉', '🍊', '🍋', '🍌', '🍍', '🥭',
            '🍎', '🍏', '🍐', '🍑', '🍒', '🍓', '🫐', '🥝', '🍅', '🫒', '🥥', '🥑', '🍆', '🥔', '🥕', '🌽',
            '🌶️', '🫑', '🥒', '🥬', '🥦', '🧄', '🧅', '🍄', '🥜', '🌰', '🍞', '🥐', '🥖', '🫓', '🥨', '🥯',
            '🥞', '🧇', '🧀', '🍖', '🍗', '🥩', '🥓', '🍔', '🍟', '🍕', '🌭', '🥪', '🌮', '🌯', '🫔', '🥙',
            '🧆', '🥚', '🍳', '🥘', '🍲', '🫕', '🥣', '🥗', '🍿', '🧈', '🧂', '🥫', '🍱', '🍘', '🍙', '🍚',
            '🍛', '🍜', '🍝', '🍠', '🍢', '🍣', '🍤', '🍥', '🥮', '🍡', '🥟', '🥠', '🥡', '🦀', '🦞', '🦐',
            '🦑', '🦪', '🍦', '🍧', '🍨', '🍩', '🍪', '🎂', '🍰', '🧁', '🥧', '🍫', '🍬', '🍭', '🍮', '🍯',
            '🍼', '🥛', '☕', '🫖', '🍵', '🍶', '🍾', '🍷', '🍸', '🍹', '🍺', '🍻', '🥂', '🥃', '🥤', '🧋',
            '🧃', '🧉', '🧊', '🥢', '🍽️', '🍴', '🥄', '🔪', '🏺', '🌍', '🌎', '🌏', '🌐', '🗺️', '🗾', '🧭',
            '🏔️', '⛰️', '🌋', '🗻', '🏕️', '🏖️', '🏜️', '🏝️', '🏞️', '🏟️', '🏛️', '🏗️', '🧱', '🏘️', '🏚️', '🏠',
            '🏡', '🏢', '🏣', '🏤', '🏥', '🏦', '🏨', '🏩', '🏪', '🏫', '🏬', '🏭', '🏮', '🏯', '🏰', '💒',
            '🗼', '🗽', '⛪', '🕌', '🛕', '🕍', '⛩️', '🕋', '⛲', '⛺', '🌉', '🌁', '🚁', '🚂', '🚃', '🚄',
            '🚅', '🚆', '🚇', '🚈', '🚉', '🚊', '🚝', '🚞', '🚋', '🚌', '🚍', '🚎', '🚐', '🚑', '🚒', '🚓',
            '🚔', '🚕', '🚖', '🚗', '🚘', '🚙', '🚚', '🚛', '🚜', '🏎️', '🏍️', '🛵', '🛺', '🚲', '🛴', '🛹',
            '🛼', '🚁', '✈️', '🛩️', '🛫', '🛬', '🪂', '💺', '🚀', '🛸', '🚉', '🚊', '🚝', '🚞', '🚋', '🚌'
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

    createImageModal() {
        // 创建图片上传模态框
        const imageModal = document.createElement('div');
        imageModal.className = 'image-upload-modal';
        imageModal.innerHTML = `
            <div class="image-upload-content">
                <h4>插入图片</h4>
                <div class="image-upload-options">
                    <button class="image-upload-btn" id="upload-file-btn">
                        <i class="fas fa-upload"></i>
                        上传文件
                    </button>
                    <div>
                        <input type="text" class="image-url-input" placeholder="输入图片URL" id="image-url-input">
                    </div>
                </div>
                <div class="image-upload-actions">
                    <button class="btn btn-secondary" id="cancel-image-btn">取消</button>
                    <button class="btn btn-primary" id="insert-image-btn">插入</button>
                </div>
            </div>
        `;

        document.body.appendChild(imageModal);
        this.imageModal = imageModal;

        // 绑定图片上传事件
        const uploadBtn = imageModal.querySelector('#upload-file-btn');
        const urlInput = imageModal.querySelector('#image-url-input');
        const insertBtn = imageModal.querySelector('#insert-image-btn');
        const cancelBtn = imageModal.querySelector('#cancel-image-btn');

        uploadBtn.addEventListener('click', () => {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = 'image/*';
            input.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) {
                    this.uploadImage(file);
                }
            });
            input.click();
        });

        insertBtn.addEventListener('click', () => {
            const url = urlInput.value.trim();
            if (url) {
                this.insertImage(url);
                this.hideImageModal();
            }
        });

        cancelBtn.addEventListener('click', () => {
            this.hideImageModal();
        });

        // 点击模态框外部关闭
        imageModal.addEventListener('click', (e) => {
            if (e.target === imageModal) {
                this.hideImageModal();
            }
        });
    }

    bindEvents() {
        // 工具栏按钮事件
        this.toolbar.addEventListener('click', (e) => {
            if (e.target.closest('.toolbar-btn[data-command]')) {
                e.preventDefault();
                const command = e.target.closest('.toolbar-btn[data-command]').dataset.command;
                this.execCommand(command);
            }
        });

        // 选择框事件
        this.toolbar.addEventListener('change', (e) => {
            if (e.target.classList.contains('toolbar-select')) {
                const command = e.target.dataset.command;
                const value = e.target.value;
                if (value) {
                    this.execCommand(command, value);
                }
            }
        });

        // 颜色选择器事件绑定
        this.setupColorPicker();

        // 表情按钮事件
        this.toolbar.addEventListener('click', (e) => {
            if (e.target.closest('.emoji-btn')) {
                e.preventDefault();
                this.toggleEmojiPicker();
            }
        });

        // 图片按钮事件
        this.toolbar.addEventListener('click', (e) => {
            if (e.target.closest('.image-btn')) {
                e.preventDefault();
                this.showImageModal();
            }
        });

        // 编辑器内容变化事件
        this.content.addEventListener('input', () => {
            this.updateToolbarState();
        });

        // 编辑器焦点事件
        this.content.addEventListener('focus', () => {
            this.updateToolbarState();
        });

        // 点击外部关闭表情选择器
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.emoji-picker') && !e.target.closest('.emoji-btn')) {
                this.emojiPicker.classList.remove('show');
            }
        });
    }

    setupColorPicker() {
        const colorTrigger = this.toolbar.querySelector('#color-picker-trigger');
        const colorInput = this.toolbar.querySelector('#color-picker-input');
        
        if (colorTrigger && colorInput) {
            // 点击按钮触发颜色选择器
            colorTrigger.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();// 确保编辑器有焦点
                this.content.focus();
                
                // 触发颜色选择器
                colorInput.click();
            });
            
            // 颜色选择器变化事件
            colorInput.addEventListener('change', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const color = e.target.value;if (color) {
                    this.applyTextColor(color);
                }
            });
            
            // 颜色选择器输入事件（实时响应）
            colorInput.addEventListener('input', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const color = e.target.value;if (color) {
                    this.applyTextColor(color);
                }
            });
        }
    }

    execCommand(command, value = null) {// 确保编辑器有焦点
        this.content.focus();
        
        // 对于颜色命令，使用特殊处理
        if (command === 'foreColor' && value) {
            this.applyTextColor(value);
        } else {
            document.execCommand(command, false, value);
        }
        
        this.updateToolbarState();
    }

    applyTextColor(color) {// 确保编辑器有焦点
        this.content.focus();
        
        // 获取当前选择
        const selection = window.getSelection();
        
        // 如果没有选中文本，选中全部文本
        if (selection.toString() === '') {
            document.execCommand('selectAll', false);
        }
        
        // 应用颜色
        const success = document.execCommand('foreColor', false, color);// 如果execCommand失败，尝试使用CSS样式
        if (!success) {
            this.applyColorWithCSS(color);
        }
        
        // 重新聚焦编辑器
        this.content.focus();
    }

    applyColorWithCSS(color) {const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            const span = document.createElement('span');
            span.style.color = color;
            
            try {
                range.surroundContents(span);
            } catch (e) {
                // 如果surroundContents失败，使用insertNode
                const contents = range.extractContents();
                span.appendChild(contents);
                range.insertNode(span);
            }
            
            // 清除选择
            selection.removeAllRanges();
        }
    }

    updateToolbarState() {
        // 更新工具栏按钮状态
        const buttons = this.toolbar.querySelectorAll('.toolbar-btn[data-command]');
        buttons.forEach(btn => {
            const command = btn.dataset.command;
            if (['bold', 'italic', 'underline', 'strikeThrough'].includes(command)) {
                btn.classList.toggle('active', document.queryCommandState(command));
            }
        });
    }

    insertEmoji(emoji) {
        this.content.focus();
        document.execCommand('insertText', false, emoji);
    }

    insertImage(url) {
        this.content.focus();
        document.execCommand('insertImage', false, url);
    }

    async uploadImage(file) {
        try {
            // 显示压缩进度
            this.showMessage('正在压缩图片...', 'info');
            
            // 压缩图片
            const compressedFile = await this.compressImage(file);
            
            // 显示上传进度
            this.showMessage('正在上传图片...', 'info');
            
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
                    // 使用服务器返回的图片URL
                    this.insertImage(result.image_url);
                    this.hideImageModal();
                    this.showMessage('图片上传成功', 'success');
                } else {
                    this.showMessage('图片上传失败: ' + result.message, 'error');
                }
            } else {
                throw new Error('上传失败');
            }
        } catch (error) {
            console.error('图片上传错误:', error);
            this.showMessage('图片上传失败，使用本地预览', 'warning');
            // 如果上传失败，使用本地预览作为备选方案
            const reader = new FileReader();
            reader.onload = (e) => {
                this.insertImage(e.target.result);
                this.hideImageModal();
            };
            reader.readAsDataURL(file);
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
                const originalSize = file.size;
                
                // 如果图片尺寸超过最大限制，按比例缩放
                if (width > maxWidth || height > maxHeight) {
                    const ratio = Math.min(maxWidth / width, maxHeight / height);
                    width = Math.floor(width * ratio);
                    height = Math.floor(height * ratio);
                }
                
                // 设置canvas尺寸
                canvas.width = width;
                canvas.height = height;
                
                // 设置图片质量，根据原图大小动态调整
                let compressionQuality = quality;
                if (originalSize > 2 * 1024 * 1024) { // 大于2MB
                    compressionQuality = 0.6;
                } else if (originalSize > 1 * 1024 * 1024) { // 大于1MB
                    compressionQuality = 0.7;
                } else if (originalSize > 500 * 1024) { // 大于500KB
                    compressionQuality = 0.8;
                }
                
                // 绘制压缩后的图片
                ctx.drawImage(img, 0, 0, width, height);
                
                // 转换为Blob
                canvas.toBlob((blob) => {
                    // 创建新的File对象，保持原文件名
                    const compressedFile = new File([blob], file.name, {
                        type: 'image/jpeg',
                        lastModified: Date.now()
                    });
                    
                    const compressionRatio = Math.round((1 - compressedFile.size / originalSize) * 100);
                    resolve(compressedFile);
                }, 'image/jpeg', compressionQuality);
            };
            
            img.onerror = () => {
                // 如果图片加载失败，返回原文件resolve(file);
            };
            
            // 加载图片
            const reader = new FileReader();
            reader.onload = (e) => {
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
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

    showImageModal() {
        this.imageModal.classList.add('show');
    }

    hideImageModal() {
        this.imageModal.classList.remove('show');
        this.imageModal.querySelector('#image-url-input').value = '';
    }

    getContent() {
        return this.content.innerHTML;
    }

    setContent(content) {
        this.content.innerHTML = content;
    }

    getTextContent() {
        return this.content.textContent || this.content.innerText || '';
    }

    clear() {
        this.content.innerHTML = '';
    }

    focus() {
        this.content.focus();
    }

    showMessage(message, type = 'info', duration = 3000) {
        if (typeof window.showToast === 'function') {
            return window.showToast(message, type, duration);
        }
        return null;
    }
}

// 导出类
window.RichTextEditor = RichTextEditor;
