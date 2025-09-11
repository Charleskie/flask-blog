/**
 * 简化版 Tiptap 编辑器
 * 不依赖外部 CDN，使用原生 contentEditable 实现
 */

class SimpleTiptapEditor {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            placeholder: '开始写作...',
            content: '',
            ...options
        };
        this.editor = null;
        this.toolbar = null;
        this.content = null;
        
        // 将编辑器实例存储到容器元素上，方便外部访问
        container.simpleTiptapEditor = this;
        this.init();
    }

    init() {
        this.createEditor();
        this.bindEvents();
    }

    createEditor() {
        // 创建编辑器HTML结构
        this.container.innerHTML = `
            <div class="tiptap-editor">
                <div class="tiptap-toolbar">
                    <div class="toolbar-group">
                        <button class="toolbar-btn" data-action="undo" title="撤销">
                            <i class="fas fa-undo"></i>
                        </button>
                        <button class="toolbar-btn" data-action="redo" title="重做">
                            <i class="fas fa-redo"></i>
                        </button>
                    </div>
                    
                    <div class="toolbar-separator"></div>
                    
                    <div class="toolbar-group">
                        <select class="toolbar-select" data-action="heading">
                            <option value="">正文</option>
                            <option value="1">标题 1</option>
                            <option value="2">标题 2</option>
                            <option value="3">标题 3</option>
                            <option value="4">标题 4</option>
                            <option value="5">标题 5</option>
                            <option value="6">标题 6</option>
                        </select>
                    </div>
                    
                    <div class="toolbar-separator"></div>
                    
                    <div class="toolbar-group">
                        <button class="toolbar-btn" data-action="bold" title="粗体">
                            <i class="fas fa-bold"></i>
                        </button>
                        <button class="toolbar-btn" data-action="italic" title="斜体">
                            <i class="fas fa-italic"></i>
                        </button>
                        <button class="toolbar-btn" data-action="underline" title="下划线">
                            <i class="fas fa-underline"></i>
                        </button>
                        <button class="toolbar-btn" data-action="strike" title="删除线">
                            <i class="fas fa-strikethrough"></i>
                        </button>
                        <button class="toolbar-btn" data-action="code" title="行内代码">
                            <i class="fas fa-code"></i>
                        </button>
                    </div>
                    
                    <div class="toolbar-separator"></div>
                    
                    <div class="toolbar-group">
                        <button class="toolbar-btn" data-action="bulletList" title="无序列表">
                            <i class="fas fa-list-ul"></i>
                        </button>
                        <button class="toolbar-btn" data-action="orderedList" title="有序列表">
                            <i class="fas fa-list-ol"></i>
                        </button>
                        <button class="toolbar-btn" data-action="taskList" title="任务列表">
                            <i class="fas fa-tasks"></i>
                        </button>
                    </div>
                    
                    <div class="toolbar-separator"></div>
                    
                    <div class="toolbar-group">
                        <button class="toolbar-btn" data-action="codeBlock" title="代码块">
                            <i class="fas fa-terminal"></i>
                        </button>
                        <select class="toolbar-select" data-action="codeBlockLanguage" title="选择编程语言">
                            <option value="javascript">JavaScript</option>
                            <option value="python">Python</option>
                            <option value="java">Java</option>
                            <option value="cpp">C++</option>
                            <option value="c">C</option>
                            <option value="html">HTML</option>
                            <option value="css">CSS</option>
                            <option value="sql">SQL</option>
                            <option value="bash">Bash</option>
                            <option value="json">JSON</option>
                            <option value="xml">XML</option>
                            <option value="markdown">Markdown</option>
                            <option value="php">PHP</option>
                            <option value="ruby">Ruby</option>
                            <option value="go">Go</option>
                            <option value="rust">Rust</option>
                            <option value="swift">Swift</option>
                            <option value="kotlin">Kotlin</option>
                            <option value="typescript">TypeScript</option>
                            <option value="text">纯文本</option>
                        </select>
                        <button class="toolbar-btn" data-action="blockquote" title="引用">
                            <i class="fas fa-quote-left"></i>
                        </button>
                        <button class="toolbar-btn" data-action="horizontalRule" title="分割线">
                            <i class="fas fa-minus"></i>
                        </button>
                    </div>
                    
                    <div class="toolbar-separator"></div>
                    
                    <div class="toolbar-group">
                        <button class="toolbar-btn" data-action="setLink" title="插入链接">
                            <i class="fas fa-link"></i>
                        </button>
                        <button class="toolbar-btn" data-action="setImage" title="插入图片">
                            <i class="fas fa-image"></i>
                        </button>
                    </div>
                    
                    <div class="toolbar-separator"></div>
                    
                    <div class="toolbar-group">
                        <button class="toolbar-btn" data-action="alignLeft" title="左对齐">
                            <i class="fas fa-align-left"></i>
                        </button>
                        <button class="toolbar-btn" data-action="alignCenter" title="居中">
                            <i class="fas fa-align-center"></i>
                        </button>
                        <button class="toolbar-btn" data-action="alignRight" title="右对齐">
                            <i class="fas fa-align-right"></i>
                        </button>
                        <button class="toolbar-btn" data-action="alignJustify" title="两端对齐">
                            <i class="fas fa-align-justify"></i>
                        </button>
                    </div>
                    
                    <div class="toolbar-separator"></div>
                    
                </div>
                
                <div class="tiptap-content" data-placeholder="${this.options.placeholder}" contenteditable="true"></div>
            </div>
        `;

        this.toolbar = this.container.querySelector('.tiptap-toolbar');
        this.content = this.container.querySelector('.tiptap-content');
        
        // 设置初始内容
        if (this.options.content) {
            this.content.innerHTML = this.options.content;
        }
        
        // 更新占位符状态
        this.updatePlaceholder();
    }

    bindEvents() {
        // 工具栏按钮事件
        this.toolbar.addEventListener('click', (e) => {
            const button = e.target.closest('.toolbar-btn');
            if (button) {
                e.preventDefault();
                const action = button.dataset.action;
                
                
                this.handleToolbarAction(action);
            }
        });

        // 选择框事件
        this.toolbar.addEventListener('change', (e) => {
            if (e.target.classList.contains('toolbar-select')) {
                const action = e.target.dataset.action;
                const value = e.target.value;
                this.handleToolbarAction(action, value);
            }
        });


        // 编辑器内容变化事件
        this.content.addEventListener('input', () => {
            this.updateToolbarState();
            this.updatePlaceholder();
            if (this.onContentChange) {
                this.onContentChange(this.getContent());
            }
        });

        // 编辑器焦点事件
        this.content.addEventListener('focus', () => {
            this.updateToolbarState();
        });

        // 键盘快捷键
        this.content.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 'b':
                        e.preventDefault();
                        this.execCommand('bold');
                        break;
                    case 'i':
                        e.preventDefault();
                        this.execCommand('italic');
                        break;
                    case 'u':
                        e.preventDefault();
                        this.execCommand('underline');
                        break;
                    case 'k':
                        e.preventDefault();
                        this.setLink();
                        break;
                }
            }
        });

        // 粘贴事件处理
        this.content.addEventListener('paste', (e) => {
            e.preventDefault();
            const text = (e.clipboardData || window.clipboardData).getData('text/plain');
            document.execCommand('insertText', false, text);
        });
    }

    handleToolbarAction(action, value = null) {
        this.content.focus();

        switch (action) {
            case 'undo':
                this.execCommand('undo');
                break;
            case 'redo':
                this.execCommand('redo');
                break;
            case 'heading':
                if (value) {
                    this.execCommand('formatBlock', `h${value}`);
                } else {
                    this.execCommand('formatBlock', 'p');
                }
                break;
            case 'bold':
                this.execCommand('bold');
                break;
            case 'italic':
                this.execCommand('italic');
                break;
            case 'underline':
                this.execCommand('underline');
                break;
            case 'strike':
                this.execCommand('strikeThrough');
                break;
            case 'code':
                this.toggleInlineCode();
                break;
            case 'bulletList':
                this.execCommand('insertUnorderedList');
                break;
            case 'orderedList':
                this.execCommand('insertOrderedList');
                break;
            case 'taskList':
                this.createTaskList();
                break;
            case 'codeBlock':
                this.insertCodeBlock();
                break;
            case 'codeBlockLanguage':
                if (value) {
                    this.insertCodeBlockWithLanguage(value);
                }
                break;
            case 'blockquote':
                this.execCommand('formatBlock', 'blockquote');
                break;
            case 'horizontalRule':
                this.execCommand('insertHorizontalRule');
                break;
            case 'setLink':
                this.setLink();
                break;
            case 'setImage':
                this.setImage();
                break;
            case 'alignLeft':
                this.execCommand('justifyLeft');
                break;
            case 'alignCenter':
                this.execCommand('justifyCenter');
                break;
            case 'alignRight':
                this.execCommand('justifyRight');
                break;
            case 'alignJustify':
                this.execCommand('justifyFull');
                break;
        }

        this.updateToolbarState();
    }

    execCommand(command, value = null) {
        this.content.focus();
        return document.execCommand(command, false, value);
    }

    setLink() {
        this.content.focus();
        const selection = window.getSelection();
        
        if (selection.rangeCount === 0) {
            alert('请先选中要设置为链接的文字');
            return;
        }
        
        const range = selection.getRangeAt(0);
        const selectedText = range.toString();
        
        if (!selectedText) {
            alert('请先选中要设置为链接的文字');
            return;
        }
        
        // 创建链接模态框
        this.showLinkModal(selectedText, '');
    }
    
    showLinkModal(text, url = '') {
        // 创建模态框
        const modal = document.createElement('div');
        modal.className = 'link-modal';
        modal.innerHTML = `
            <div class="link-modal-overlay">
                <div class="link-modal-content">
                    <div class="link-modal-header">
                        <h3>插入链接</h3>
                        <button class="link-modal-close">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="link-modal-body">
                        <div class="form-group">
                            <label for="link-text">显示文字:</label>
                            <input type="text" id="link-text" value="${text}" placeholder="链接显示的文字">
                        </div>
                        <div class="form-group">
                            <label for="link-url">链接地址:</label>
                            <input type="url" id="link-url" value="${url}" placeholder="https://example.com">
                        </div>
                    </div>
                    <div class="link-modal-footer">
                        <button class="btn btn-secondary link-modal-cancel">取消</button>
                        <button class="btn btn-primary link-modal-confirm">确定</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // 显示模态框
        setTimeout(() => {
            modal.classList.add('show');
        }, 10);
        
        // 绑定事件
        this.bindLinkModalEvents(modal);
    }
    
    bindLinkModalEvents(modal) {
        const closeModal = () => {
            modal.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(modal);
            }, 300);
        };
        
        // 关闭按钮
        modal.querySelector('.link-modal-close').addEventListener('click', closeModal);
        modal.querySelector('.link-modal-cancel').addEventListener('click', closeModal);
        
        // 点击背景关闭
        modal.querySelector('.link-modal-overlay').addEventListener('click', (e) => {
            if (e.target === modal.querySelector('.link-modal-overlay')) {
                closeModal();
            }
        });
        
        // 确认按钮
        modal.querySelector('.link-modal-confirm').addEventListener('click', () => {
            const text = modal.querySelector('#link-text').value.trim();
            const url = modal.querySelector('#link-url').value.trim();
            
            if (!text) {
                alert('请输入显示文字');
                return;
            }
            
            if (!url) {
                alert('请输入链接地址');
                return;
            }
            
            // 验证URL格式
            try {
                new URL(url);
            } catch (e) {
                alert('请输入有效的链接地址');
                return;
            }
            
            this.insertLink(text, url);
            closeModal();
        });
        
        // ESC键关闭
        const handleKeyDown = (e) => {
            if (e.key === 'Escape') {
                closeModal();
                document.removeEventListener('keydown', handleKeyDown);
            }
        };
        document.addEventListener('keydown', handleKeyDown);
    }
    
    insertLink(text, url) {
        const selection = window.getSelection();
        const range = selection.getRangeAt(0);
        
        // 创建链接元素
        const linkElement = document.createElement('a');
        linkElement.href = url;
        linkElement.textContent = text;
        linkElement.target = '_blank';
        linkElement.rel = 'noopener noreferrer';
        
        // 替换选中的文本
        range.deleteContents();
        range.insertNode(linkElement);
        
        // 选中新创建的链接
        range.selectNode(linkElement);
        selection.removeAllRanges();
        selection.addRange(range);
        
        this.onContentChange();
    }

    setImage() {
        this.showImageModal();
    }

    createTaskList() {
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            const listItem = document.createElement('li');
            listItem.innerHTML = '☐ 任务项';
            listItem.style.listStyle = 'none';
            listItem.style.marginLeft = '20px';
            
            range.deleteContents();
            range.insertNode(listItem);
            
            // 移动光标到任务项后面
            range.setStartAfter(listItem);
            range.setEndAfter(listItem);
            selection.removeAllRanges();
            selection.addRange(range);
        }
    }

    updateToolbarState() {
        // 更新按钮状态
        const buttons = this.toolbar.querySelectorAll('.toolbar-btn');
        buttons.forEach(btn => {
            const action = btn.dataset.action;
            let isActive = false;

            switch (action) {
                case 'bold':
                    isActive = document.queryCommandState('bold');
                    break;
                case 'italic':
                    isActive = document.queryCommandState('italic');
                    break;
                case 'underline':
                    isActive = document.queryCommandState('underline');
                    break;
                case 'strike':
                    isActive = document.queryCommandState('strikeThrough');
                    break;
                case 'bulletList':
                    isActive = document.queryCommandState('insertUnorderedList');
                    break;
                case 'orderedList':
                    isActive = document.queryCommandState('insertOrderedList');
                    break;
                case 'alignLeft':
                    isActive = document.queryCommandState('justifyLeft');
                    break;
                case 'alignCenter':
                    isActive = document.queryCommandState('justifyCenter');
                    break;
                case 'alignRight':
                    isActive = document.queryCommandState('justifyRight');
                    break;
                case 'alignJustify':
                    isActive = document.queryCommandState('justifyFull');
                    break;
            }

            btn.classList.toggle('active', isActive);
        });

        // 更新标题选择框
        const headingSelect = this.toolbar.querySelector('[data-action="heading"]');
        if (headingSelect) {
            const selection = window.getSelection();
            if (selection.rangeCount > 0) {
                const range = selection.getRangeAt(0);
                const element = range.commonAncestorContainer.nodeType === Node.TEXT_NODE 
                    ? range.commonAncestorContainer.parentElement 
                    : range.commonAncestorContainer;
                
                const tagName = element.tagName ? element.tagName.toLowerCase() : '';
                if (tagName.match(/^h[1-6]$/)) {
                    headingSelect.value = tagName.charAt(1);
                } else {
                    headingSelect.value = '';
                }
            }
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
        this.updateToolbarState();
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
        img.style.maxWidth = '100%';
        img.style.height = 'auto';
        img.style.borderRadius = '6px';
        img.style.margin = '4px 0';
        img.style.display = 'block';
        img.style.transition = 'all 0.2s ease';
        
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


    toggleInlineCode() {
        this.content.focus();
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            const selectedText = range.toString();
            
            if (selectedText) {
                // 如果有选中文本，用<code>标签包装
                const codeElement = document.createElement('code');
                codeElement.textContent = selectedText;
                range.deleteContents();
                range.insertNode(codeElement);
                
                // 选中插入的代码元素
                range.selectNode(codeElement);
                selection.removeAllRanges();
                selection.addRange(range);
            } else {
                // 如果没有选中文本，插入代码标签
                const codeElement = document.createElement('code');
                codeElement.textContent = '代码';
                range.insertNode(codeElement);
                
                // 选中插入的代码元素内容
                range.selectNodeContents(codeElement);
                selection.removeAllRanges();
                selection.addRange(range);
            }
        }
        this.onContentChange();
    }

    insertCodeBlock() {
        this.content.focus();
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            const selectedText = range.toString();
            
            // 创建代码块
            const preElement = document.createElement('pre');
            const codeElement = document.createElement('code');
            
            // 设置语言（默认为javascript）
            preElement.setAttribute('data-language', 'javascript');
            
            if (selectedText) {
                // 如果有选中文本，将其放入代码块
                codeElement.textContent = selectedText;
            } else {
                // 如果没有选中文本，插入示例代码
                codeElement.textContent = '// 在这里输入你的代码\nconsole.log("Hello, World!");';
            }
            
            preElement.appendChild(codeElement);
            range.deleteContents();
            range.insertNode(preElement);
            
            // 选中代码块内容
            range.selectNodeContents(codeElement);
            selection.removeAllRanges();
            selection.addRange(range);
        }
        this.onContentChange();
    }
    
    insertCodeBlockWithLanguage(language = 'javascript') {
        this.content.focus();
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            const selectedText = range.toString();
            
            // 创建代码块
            const preElement = document.createElement('pre');
            const codeElement = document.createElement('code');
            
            // 设置语言
            preElement.setAttribute('data-language', language);
            
            if (selectedText) {
                // 如果有选中文本，将其放入代码块
                codeElement.textContent = selectedText;
            } else {
                // 根据语言插入示例代码
                codeElement.textContent = this.getExampleCode(language);
            }
            
            preElement.appendChild(codeElement);
            range.deleteContents();
            range.insertNode(preElement);
            
            // 选中代码块内容
            range.selectNodeContents(codeElement);
            selection.removeAllRanges();
            selection.addRange(range);
        }
        this.onContentChange();
    }
    
    getExampleCode(language) {
        const examples = {
            'javascript': '// JavaScript 示例\nconsole.log("Hello, World!");\n\nfunction greet(name) {\n    return `Hello, ${name}!`;\n}',
            'python': '# Python 示例\nprint("Hello, World!")\n\ndef greet(name):\n    return f"Hello, {name}!"',
            'java': '// Java 示例\npublic class HelloWorld {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}',
            'cpp': '// C++ 示例\n#include <iostream>\n\nint main() {\n    std::cout << "Hello, World!" << std::endl;\n    return 0;\n}',
            'c': '// C 示例\n#include <stdio.h>\n\nint main() {\n    printf("Hello, World!\\n");\n    return 0;\n}',
            'html': '<!-- HTML 示例 -->\n<!DOCTYPE html>\n<html>\n<head>\n    <title>Hello World</title>\n</head>\n<body>\n    <h1>Hello, World!</h1>\n</body>\n</html>',
            'css': '/* CSS 示例 */\nbody {\n    font-family: Arial, sans-serif;\n    margin: 0;\n    padding: 20px;\n}\n\nh1 {\n    color: #333;\n    text-align: center;\n}',
            'sql': '-- SQL 示例\nSELECT * FROM users \nWHERE age > 18 \nORDER BY name;\n\nINSERT INTO users (name, age) \nVALUES (\'John\', 25);',
            'bash': '# Bash 示例\necho "Hello, World!"\n\n# 列出文件\nls -la\n\n# 创建目录\nmkdir new_folder',
            'json': '{\n  "name": "Hello World",\n  "version": "1.0.0",\n  "description": "A simple example",\n  "main": "index.js",\n  "scripts": {\n    "start": "node index.js"\n  }\n}',
            'xml': '<?xml version="1.0" encoding="UTF-8"?>\n<root>\n    <message>Hello, World!</message>\n    <items>\n        <item id="1">First item</item>\n        <item id="2">Second item</item>\n    </items>\n</root>',
            'markdown': '# Markdown 示例\n\n## 标题\n\n这是一段**粗体**文字和*斜体*文字。\n\n- 列表项 1\n- 列表项 2\n\n```javascript\nconsole.log("代码块");\n```',
            'php': '<?php\n// PHP 示例\necho "Hello, World!";\n\nfunction greet($name) {\n    return "Hello, " . $name . "!";\n}\n\n$message = greet("World");\necho $message;\n?>',
            'ruby': '# Ruby 示例\nputs "Hello, World!"\n\ndef greet(name)\n  "Hello, #{name}!"\nend\n\nputs greet("World")',
            'go': 'package main\n\nimport "fmt"\n\nfunc main() {\n    fmt.Println("Hello, World!")\n}\n\nfunc greet(name string) string {\n    return fmt.Sprintf("Hello, %s!", name)\n}',
            'rust': '// Rust 示例\nfn main() {\n    println!("Hello, World!");\n}\n\nfn greet(name: &str) -> String {\n    format!("Hello, {}!", name)\n}',
            'swift': '// Swift 示例\nimport Foundation\n\nprint("Hello, World!")\n\nfunc greet(name: String) -> String {\n    return "Hello, \\(name)!"\n}\n\nlet message = greet(name: "World")\nprint(message)',
            'kotlin': '// Kotlin 示例\nfun main() {\n    println("Hello, World!")\n}\n\nfun greet(name: String): String {\n    return "Hello, $name!"\n}',
            'typescript': '// TypeScript 示例\nconsole.log("Hello, World!");\n\ninterface Person {\n    name: string;\n    age: number;\n}\n\nfunction greet(person: Person): string {\n    return `Hello, ${person.name}!`;\n}',
            'text': '纯文本示例\n\n这里可以输入任何文本内容，\n支持多行文本。\n\n可以用于：\n- 笔记\n- 说明\n- 文档'
        };
        
        return examples[language] || examples['text'];
    }
    

    makeImageResizable(img) {
        // 检查图片是否在DOM中
        if (!img.parentNode) {
            console.warn('图片尚未插入到DOM中，无法添加调整大小功能');
            return;
        }
        
        // 创建包装容器
        const wrapper = document.createElement('div');
        wrapper.className = 'image-resize-wrapper';
        wrapper.style.position = 'relative';
        wrapper.style.display = 'inline-block';
        wrapper.style.maxWidth = '100%';
        
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
                    
                    // 限制最大尺寸（不超过编辑器宽度）
                    const maxWidth = this.content.offsetWidth - 32; // 留出边距
                    newWidth = Math.min(newWidth, maxWidth);
                    
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
            this.content.removeEventListener('input', this.updateToolbarState);
            this.content.removeEventListener('focus', this.updateToolbarState);
        }
    }
}

// 导出类
window.SimpleTiptapEditor = SimpleTiptapEditor;
