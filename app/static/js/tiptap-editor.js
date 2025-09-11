/**
 * Tiptap 富文本编辑器
 * 基于 Tiptap 核心库实现的现代化编辑器
 */

class TiptapEditor {
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
        container.tiptapEditor = this;
        this.init();
    }

    async init() {
        // 动态加载 Tiptap 核心库
        await this.loadTiptapLibraries();
        this.createEditor();
        this.bindEvents();
    }

    async loadTiptapLibraries() {
        // 检查是否已经加载
        if (window.TiptapCore && window.TiptapStarterKit) {
            return;
        }

        // 动态加载 Tiptap 核心库
        const loadScript = (src) => {
            return new Promise((resolve, reject) => {
                const script = document.createElement('script');
                script.src = src;
                script.onload = resolve;
                script.onerror = (error) => {
                    console.warn(`Failed to load script: ${src}`, error);
                    reject(error);
                };
                document.head.appendChild(script);
            });
        };

        // 使用多个 CDN 源作为备选
        const cdnSources = [
            'https://unpkg.com',
            'https://cdn.jsdelivr.net/npm',
            'https://cdnjs.cloudflare.com/ajax/libs'
        ];

        const libraries = [
            '@tiptap/core@2.1.13/dist/index.umd.js',
            '@tiptap/pm@2.1.13/dist/index.umd.js',
            '@tiptap/starter-kit@2.1.13/dist/index.umd.js',
            '@tiptap/extension-text-align@2.1.13/dist/index.umd.js',
            '@tiptap/extension-underline@2.1.13/dist/index.umd.js',
            '@tiptap/extension-link@2.1.13/dist/index.umd.js',
            '@tiptap/extension-image@2.1.13/dist/index.umd.js',
            '@tiptap/extension-color@2.1.13/dist/index.umd.js',
            '@tiptap/extension-text-style@2.1.13/dist/index.umd.js',
            '@tiptap/extension-highlight@2.1.13/dist/index.umd.js'
        ];

        try {
            // 尝试加载每个库
            for (const lib of libraries) {
                let loaded = false;
                for (const cdn of cdnSources) {
                    try {
                        await loadScript(`${cdn}/${lib}`);
                        loaded = true;
                        break;
                    } catch (error) {
                        console.warn(`Failed to load ${lib} from ${cdn}`);
                    }
                }
                
                if (!loaded) {
                    throw new Error(`Failed to load ${lib} from all CDN sources`);
                }
            }
        } catch (error) {
            console.error('Failed to load Tiptap libraries:', error);
            // 如果所有 CDN 都失败，尝试使用简化版本
            await this.loadFallbackLibraries();
        }
    }

    async loadFallbackLibraries() {
        console.log('Loading fallback Tiptap libraries...');
        
        // 创建一个简化的编辑器实现
        window.TiptapCore = {
            Editor: class FallbackEditor {
                constructor(options) {
                    this.element = options.element;
                    this.content = options.content || '';
                    this.extensions = options.extensions || [];
                    this.onUpdate = options.onUpdate;
                    this.onSelectionUpdate = options.onSelectionUpdate;
                    
                    this.init();
                }
                
                init() {
                    this.element.innerHTML = this.content;
                    this.element.contentEditable = true;
                    this.element.addEventListener('input', () => {
                        if (this.onUpdate) {
                            this.onUpdate({ editor: this });
                        }
                    });
                }
                
                getHTML() {
                    return this.element.innerHTML;
                }
                
                getText() {
                    return this.element.textContent || this.element.innerText || '';
                }
                
                commands = {
                    setContent: (content) => {
                        this.element.innerHTML = content;
                    },
                    clearContent: () => {
                        this.element.innerHTML = '';
                    },
                    focus: () => {
                        this.element.focus();
                    }
                };
                
                chain() {
                    return {
                        focus: () => ({
                            toggleBold: () => ({ run: () => this.execCommand('bold') }),
                            toggleItalic: () => ({ run: () => this.execCommand('italic') }),
                            toggleUnderline: () => ({ run: () => this.execCommand('underline') }),
                            toggleStrike: () => ({ run: () => this.execCommand('strikeThrough') }),
                            toggleCode: () => ({ run: () => this.execCommand('code') }),
                            toggleBulletList: () => ({ run: () => this.execCommand('insertUnorderedList') }),
                            toggleOrderedList: () => ({ run: () => this.execCommand('insertOrderedList') }),
                            toggleTaskList: () => ({ run: () => this.execCommand('insertUnorderedList') }),
                            toggleCodeBlock: () => ({ run: () => this.execCommand('formatBlock', 'pre') }),
                            toggleBlockquote: () => ({ run: () => this.execCommand('formatBlock', 'blockquote') }),
                            setHorizontalRule: () => ({ run: () => this.execCommand('insertHorizontalRule') }),
                            setLink: (options) => ({ run: () => this.setLink(options) }),
                            setImage: (options) => ({ run: () => this.setImage(options) }),
                            setTextAlign: (align) => ({ run: () => this.setTextAlign(align) }),
                            setColor: (color) => ({ run: () => this.setColor(color) }),
                            toggleHighlight: () => ({ run: () => this.toggleHighlight() }),
                            toggleHeading: (level) => ({ run: () => this.execCommand('formatBlock', `h${level}`) }),
                            setParagraph: () => ({ run: () => this.execCommand('formatBlock', 'p') }),
                            undo: () => ({ run: () => this.execCommand('undo') }),
                            redo: () => ({ run: () => this.execCommand('redo') })
                        })
                    };
                }
                
                execCommand(command, value = null) {
                    document.execCommand(command, false, value);
                }
                
                setLink(options) {
                    const url = prompt('请输入链接地址:', options?.href || '');
                    if (url) {
                        this.execCommand('createLink', url);
                    }
                }
                
                setImage(options) {
                    const url = prompt('请输入图片地址:', options?.src || '');
                    if (url) {
                        this.execCommand('insertImage', url);
                    }
                }
                
                setTextAlign(align) {
                    this.execCommand('justifyLeft');
                    if (align === 'center') this.execCommand('justifyCenter');
                    if (align === 'right') this.execCommand('justifyRight');
                    if (align === 'justify') this.execCommand('justifyFull');
                }
                
                setColor(color) {
                    this.execCommand('foreColor', color);
                }
                
                toggleHighlight() {
                    this.execCommand('backColor', '#ffff00');
                }
                
                isActive(type, attrs = {}) {
                    return document.queryCommandState(type === 'bold' ? 'bold' : 
                                                    type === 'italic' ? 'italic' : 
                                                    type === 'underline' ? 'underline' : 
                                                    type === 'strike' ? 'strikeThrough' : false);
                }
                
                destroy() {
                    // 清理资源
                }
            }
        };
        
        // 创建简化的扩展
        window.TiptapStarterKit = {
            StarterKit: class StarterKit {}
        };
        
        window.TiptapTextAlign = {
            TextAlign: class TextAlign {}
        };
        
        window.TiptapUnderline = {
            Underline: class Underline {}
        };
        
        window.TiptapLink = {
            Link: class Link {}
        };
        
        window.TiptapImage = {
            Image: class Image {}
        };
        
        window.TiptapColor = {
            Color: class Color {}
        };
        
        window.TiptapTextStyle = {
            TextStyle: class TextStyle {}
        };
        
        window.TiptapHighlight = {
            Highlight: class Highlight {}
        };
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
                    
                    <div class="toolbar-group">
                        <input type="color" class="color-picker" data-action="setColor" title="文字颜色" value="#000000">
                        <button class="toolbar-btn" data-action="setHighlight" title="高亮">
                            <i class="fas fa-highlighter"></i>
                        </button>
                    </div>
                </div>
                
                <div class="tiptap-content" data-placeholder="${this.options.placeholder}"></div>
            </div>
        `;

        this.toolbar = this.container.querySelector('.tiptap-toolbar');
        this.content = this.container.querySelector('.tiptap-content');
        
        // 初始化 Tiptap 编辑器
        this.initTiptapEditor();
    }

    initTiptapEditor() {
        const { Editor } = window.TiptapCore;
        const { StarterKit } = window.TiptapStarterKit;
        const { TextAlign } = window.TiptapTextAlign;
        const { Underline } = window.TiptapUnderline;
        const { Link } = window.TiptapLink;
        const { Image } = window.TiptapImage;
        const { Color } = window.TiptapColor;
        const { TextStyle } = window.TiptapTextStyle;
        const { Highlight } = window.TiptapHighlight;

        this.editor = new Editor({
            element: this.content,
            extensions: [
                StarterKit.configure({
                    bulletList: {
                        keepMarks: true,
                        keepAttributes: false,
                    },
                    orderedList: {
                        keepMarks: true,
                        keepAttributes: false,
                    },
                }),
                TextAlign.configure({
                    types: ['heading', 'paragraph'],
                }),
                Underline,
                Link.configure({
                    openOnClick: false,
                    HTMLAttributes: {
                        class: 'tiptap-link',
                    },
                }),
                Image.configure({
                    HTMLAttributes: {
                        class: 'tiptap-image',
                    },
                }),
                Color,
                TextStyle,
                Highlight.configure({
                    multicolor: true,
                }),
            ],
            content: this.options.content,
            onUpdate: ({ editor }) => {
                this.updateToolbarState();
                this.onContentChange && this.onContentChange(editor.getHTML());
            },
            onSelectionUpdate: ({ editor }) => {
                this.updateToolbarState();
            },
        });

        // 设置占位符
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

        // 颜色选择器事件
        this.toolbar.addEventListener('change', (e) => {
            if (e.target.classList.contains('color-picker')) {
                const color = e.target.value;
                this.handleToolbarAction('setColor', color);
            }
        });

        // 键盘快捷键
        this.content.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 'b':
                        e.preventDefault();
                        this.editor.chain().focus().toggleBold().run();
                        break;
                    case 'i':
                        e.preventDefault();
                        this.editor.chain().focus().toggleItalic().run();
                        break;
                    case 'u':
                        e.preventDefault();
                        this.editor.chain().focus().toggleUnderline().run();
                        break;
                    case 'k':
                        e.preventDefault();
                        this.setLink();
                        break;
                }
            }
        });
    }

    handleToolbarAction(action, value = null) {
        if (!this.editor) return;

        this.editor.chain().focus();

        switch (action) {
            case 'undo':
                this.editor.chain().undo().run();
                break;
            case 'redo':
                this.editor.chain().redo().run();
                break;
            case 'heading':
                if (value) {
                    this.editor.chain().toggleHeading({ level: parseInt(value) }).run();
                } else {
                    this.editor.chain().setParagraph().run();
                }
                break;
            case 'bold':
                this.editor.chain().toggleBold().run();
                break;
            case 'italic':
                this.editor.chain().toggleItalic().run();
                break;
            case 'underline':
                this.editor.chain().toggleUnderline().run();
                break;
            case 'strike':
                this.editor.chain().toggleStrike().run();
                break;
            case 'code':
                this.editor.chain().toggleCode().run();
                break;
            case 'bulletList':
                this.editor.chain().toggleBulletList().run();
                break;
            case 'orderedList':
                this.editor.chain().toggleOrderedList().run();
                break;
            case 'taskList':
                this.editor.chain().toggleTaskList().run();
                break;
            case 'codeBlock':
                this.editor.chain().toggleCodeBlock().run();
                break;
            case 'blockquote':
                this.editor.chain().toggleBlockquote().run();
                break;
            case 'horizontalRule':
                this.editor.chain().setHorizontalRule().run();
                break;
            case 'setLink':
                this.setLink();
                break;
            case 'setImage':
                this.setImage();
                break;
            case 'alignLeft':
                this.editor.chain().setTextAlign('left').run();
                break;
            case 'alignCenter':
                this.editor.chain().setTextAlign('center').run();
                break;
            case 'alignRight':
                this.editor.chain().setTextAlign('right').run();
                break;
            case 'alignJustify':
                this.editor.chain().setTextAlign('justify').run();
                break;
            case 'setColor':
                if (value) {
                    this.editor.chain().setColor(value).run();
                }
                break;
            case 'setHighlight':
                this.editor.chain().toggleHighlight().run();
                break;
        }

        this.updateToolbarState();
    }

    setLink() {
        const url = window.prompt('请输入链接地址:');
        if (url) {
            this.editor.chain().focus().setLink({ href: url }).run();
        }
    }

    async setImage() {
        const url = window.prompt('请输入图片地址:');
        if (url) {
            this.editor.chain().focus().setImage({ src: url }).run();
        }
    }

    updateToolbarState() {
        if (!this.editor) return;

        // 更新按钮状态
        const buttons = this.toolbar.querySelectorAll('.toolbar-btn');
        buttons.forEach(btn => {
            const action = btn.dataset.action;
            let isActive = false;

            switch (action) {
                case 'bold':
                    isActive = this.editor.isActive('bold');
                    break;
                case 'italic':
                    isActive = this.editor.isActive('italic');
                    break;
                case 'underline':
                    isActive = this.editor.isActive('underline');
                    break;
                case 'strike':
                    isActive = this.editor.isActive('strike');
                    break;
                case 'code':
                    isActive = this.editor.isActive('code');
                    break;
                case 'bulletList':
                    isActive = this.editor.isActive('bulletList');
                    break;
                case 'orderedList':
                    isActive = this.editor.isActive('orderedList');
                    break;
                case 'taskList':
                    isActive = this.editor.isActive('taskList');
                    break;
                case 'codeBlock':
                    isActive = this.editor.isActive('codeBlock');
                    break;
                case 'blockquote':
                    isActive = this.editor.isActive('blockquote');
                    break;
                case 'alignLeft':
                    isActive = this.editor.isActive({ textAlign: 'left' });
                    break;
                case 'alignCenter':
                    isActive = this.editor.isActive({ textAlign: 'center' });
                    break;
                case 'alignRight':
                    isActive = this.editor.isActive({ textAlign: 'right' });
                    break;
                case 'alignJustify':
                    isActive = this.editor.isActive({ textAlign: 'justify' });
                    break;
                case 'setHighlight':
                    isActive = this.editor.isActive('highlight');
                    break;
            }

            btn.classList.toggle('active', isActive);
        });

        // 更新标题选择框
        const headingSelect = this.toolbar.querySelector('[data-action="heading"]');
        if (headingSelect) {
            for (let i = 1; i <= 6; i++) {
                if (this.editor.isActive('heading', { level: i })) {
                    headingSelect.value = i.toString();
                    return;
                }
            }
            headingSelect.value = '';
        }
    }

    updatePlaceholder() {
        if (!this.editor) return;
        
        const isEmpty = this.editor.isEmpty;
        this.content.classList.toggle('is-empty', isEmpty);
    }

    getContent() {
        return this.editor ? this.editor.getHTML() : '';
    }

    setContent(content) {
        if (this.editor) {
            this.editor.commands.setContent(content);
        }
    }

    getTextContent() {
        return this.editor ? this.editor.getText() : '';
    }

    clear() {
        if (this.editor) {
            this.editor.commands.clearContent();
        }
    }

    focus() {
        if (this.editor) {
            this.editor.commands.focus();
        }
    }

    destroy() {
        if (this.editor) {
            this.editor.destroy();
        }
    }
}

// 导出类
window.TiptapEditor = TiptapEditor;
