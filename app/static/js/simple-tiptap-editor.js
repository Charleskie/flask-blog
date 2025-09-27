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
                        <button class="toolbar-btn" data-action="insertImage" title="插入图片">
                            <i class="fas fa-image"></i>
                        </button>
                    </div>
                    
                    <div class="toolbar-separator"></div>
                    
        <div class="toolbar-group">
            <button class="toolbar-btn" data-action="insertTable" title="插入表格">
                <i class="fas fa-table"></i>
            </button>
            <button class="toolbar-btn" data-action="addTableRow" title="添加行">
                <i class="fas fa-plus"></i><i class="fas fa-grip-lines-vertical"></i>
            </button>
            <button class="toolbar-btn" data-action="addTableColumn" title="添加列">
                <i class="fas fa-plus"></i><i class="fas fa-grip-lines"></i>
            </button>
            <button class="toolbar-btn" data-action="deleteTableRow" title="删除行">
                <i class="fas fa-minus"></i><i class="fas fa-grip-lines-vertical"></i>
            </button>
            <button class="toolbar-btn" data-action="deleteTableColumn" title="删除列">
                <i class="fas fa-minus"></i><i class="fas fa-grip-lines"></i>
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

        // 键盘快捷键和光标导航
        this.content.addEventListener('keydown', (e) => {
            // 处理光标导航
            this.handleSimpleCursorNavigation(e);
            
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

        // 链接点击事件处理
        this.content.addEventListener('click', (e) => {
            if (e.target.tagName === 'A' && e.target.classList.contains('tiptap-link')) {
                console.log('检测到链接点击事件');
                e.preventDefault();
                const url = e.target.href;
                console.log(`打开链接: ${url}`);
                window.open(url, '_blank');
            }
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
            case 'insertImage':
                this.insertImage();
                break;
            case 'insertTable':
                this.insertTable();
                break;
            case 'addTableRow':
                this.addTableRow();
                break;
            case 'addTableColumn':
                this.addTableColumn();
                break;
            case 'deleteTableRow':
                this.deleteTableRow();
                break;
            case 'deleteTableColumn':
                this.deleteTableColumn();
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
    
    handleSimpleCursorNavigation(e) {
        const selection = window.getSelection();
        if (selection.rangeCount === 0) return;
        
        const range = selection.getRangeAt(0);
        const container = range.commonAncestorContainer;
        
        // 检查是否在行内代码中
        const inlineCode = this.findParentElement(container, 'code');
        // 检查是否在代码块中
        const codeBlock = this.findParentElement(container, 'pre');
        
        console.log('光标导航检查:', { 
            key: e.key, 
            inlineCode: !!inlineCode, 
            codeBlock: !!codeBlock,
            endContainer: range.endContainer.nodeType,
            endOffset: range.endOffset,
            container: container,
            containerType: container.nodeType,
            containerText: container.textContent ? container.textContent.substring(0, 20) : 'N/A',
            parentNode: container.parentNode,
            parentTagName: container.parentNode ? container.parentNode.tagName : 'N/A'
        });
        
        // 行内代码退出逻辑
        if (inlineCode && !codeBlock) {
            if (e.key === 'ArrowRight' || e.key === ' ') {
                const endContainer = range.endContainer;
                const endOffset = range.endOffset;
                
                console.log('行内代码检查:', {
                    endContainer: endContainer.nodeType,
                    endOffset: endOffset,
                    textLength: endContainer.textContent ? endContainer.textContent.length : 0,
                    isLastChild: endContainer === inlineCode.lastChild
                });
                
                // 检查是否在行内代码的末尾
                if (endContainer.nodeType === Node.TEXT_NODE && 
                    endContainer === inlineCode.lastChild && 
                    endOffset === endContainer.textContent.length) {
                    
                    console.log('触发行内代码退出');
                    e.preventDefault();
                    this.exitInlineCodeTiptapStyle(inlineCode);
                }
            }
        }
        
        // 代码块退出逻辑
        if (codeBlock) {
            // 处理三次回车退出
            if (e.key === 'Enter') {
                if (!this.enterCount) this.enterCount = 0;
                this.enterCount++;
                
                console.log('代码块回车计数:', this.enterCount);
                
                // 检查是否在代码块的末尾
                const endContainer = range.endContainer;
                const endOffset = range.endOffset;
                
                if (endContainer.nodeType === Node.TEXT_NODE) {
                    const textContent = endContainer.textContent;
                    const lastNewlineIndex = textContent.lastIndexOf('\n');
                    
                    console.log('代码块检查:', {
                        lastNewlineIndex: lastNewlineIndex,
                        endOffset: endOffset,
                        isAtEnd: lastNewlineIndex === -1 || endOffset > lastNewlineIndex
                    });
                    
                    // 如果光标在最后一行且连续按了三次回车
                    if ((lastNewlineIndex === -1 || endOffset > lastNewlineIndex) && this.enterCount >= 3) {
                        console.log('触发代码块退出（三次回车）');
                        e.preventDefault();
                        this.exitCodeBlockTiptapStyle(codeBlock);
                        this.enterCount = 0;
                    }
                }
            } else {
                // 重置回车计数
                this.enterCount = 0;
            }
            
            // 处理向下箭头退出
            if (e.key === 'ArrowDown') {
                const endContainer = range.endContainer;
                const endOffset = range.endOffset;
                
                // 检查是否在代码块的末尾
                if (endContainer.nodeType === Node.TEXT_NODE) {
                    const textContent = endContainer.textContent;
                    const lastNewlineIndex = textContent.lastIndexOf('\n');
                    
                    // 如果光标在最后一行
                    if (lastNewlineIndex === -1 || endOffset > lastNewlineIndex) {
                        console.log('触发代码块退出（向下箭头）');
                        e.preventDefault();
                        this.exitCodeBlockTiptapStyle(codeBlock);
                    }
                }
            }
        }
    }
    
    exitInlineCodeTiptapStyle(inlineCode) {
        console.log('Tiptap风格退出行内代码');
        
        // 在行内代码后面插入一个零宽空格字符，防止浏览器合并文本节点
        const textNode = document.createTextNode('\u200B'); // 零宽空格
        inlineCode.parentNode.insertBefore(textNode, inlineCode.nextSibling);
        
        // 将光标移动到新插入的文本节点
        const range = document.createRange();
        range.setStart(textNode, 0);
        range.setEnd(textNode, 0);
        
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        
        // 触发内容变化
        if (this.onContentChange) {
            this.onContentChange(this.getContent());
        }
        
        console.log('行内代码退出完成');
    }
    
    exitCodeBlockTiptapStyle(codeBlock) {
        console.log('Tiptap风格退出代码块');
        
        // 在代码块后面插入一个段落
        const paragraph = document.createElement('p');
        const br = document.createElement('br');
        paragraph.appendChild(br);
        
        codeBlock.parentNode.insertBefore(paragraph, codeBlock.nextSibling);
        
        // 将光标移动到新插入的段落
        const range = document.createRange();
        range.setStart(paragraph, 0);
        range.setEnd(paragraph, 0);
        
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        
        // 触发内容变化
        if (this.onContentChange) {
            this.onContentChange(this.getContent());
        }
        
        console.log('代码块退出完成');
    }
    
    handleCursorNavigation(e) {
        const selection = window.getSelection();
        if (selection.rangeCount === 0) return;
        
        const range = selection.getRangeAt(0);
        const container = range.commonAncestorContainer;
        
        // 检查是否在行内代码中
        const inlineCode = this.findParentElement(container, 'code');
        // 检查是否在代码块中
        const codeBlock = this.findParentElement(container, 'pre');
        
        console.log('光标导航检查:', { 
            inlineCode: !!inlineCode, 
            codeBlock: !!codeBlock, 
            key: e.key 
        });
        
        if (inlineCode && !codeBlock) {
            // 在行内代码中
            this.handleInlineCodeNavigation(e, inlineCode, range);
        } else if (codeBlock) {
            // 在代码块中
            this.handleCodeBlockNavigation(e, codeBlock, range);
        }
    }
    
    findParentElement(node, tagName) {
        let current = node;
        
        // 如果是文本节点，先找到父元素
        while (current && current.nodeType !== Node.ELEMENT_NODE) {
            current = current.parentNode;
        }
        
        // 从当前元素开始查找（包括当前元素）
        while (current) {
            if (current.tagName && current.tagName.toLowerCase() === tagName.toLowerCase()) {
                return current;
            }
            current = current.parentNode;
        }
        return null;
    }
    
    handleInlineCodeNavigation(e, inlineCode, range) {
        console.log('处理行内代码导航:', e.key);
        
        if (e.key === 'ArrowRight') {
            // 检查光标是否在行内代码的末尾
            if (this.isAtEndOfElement(range, inlineCode)) {
                console.log('光标在行内代码末尾，按右箭头');
                e.preventDefault();
                this.exitInlineCodeAfter(inlineCode, range);
            }
        } else if (e.key === 'ArrowLeft') {
            // 检查光标是否在行内代码的开头
            if (this.isAtStartOfElement(range, inlineCode)) {
                console.log('光标在行内代码开头，按左箭头');
                e.preventDefault();
                this.exitInlineCodeBefore(inlineCode, range);
            }
        }
    }
    
    handleCodeBlockNavigation(e, codeBlock, range) {
        console.log('处理代码块导航:', e.key);
        
        if (e.key === 'ArrowDown') {
            // 检查光标是否在代码块的最后一行
            if (this.isAtLastLineOfCodeBlock(range, codeBlock)) {
                console.log('光标在代码块最后一行，按下箭头');
                e.preventDefault();
                this.exitCodeBlockAfter(codeBlock, range);
            }
        } else if (e.key === 'ArrowUp') {
            // 检查光标是否在代码块的第一行
            if (this.isAtFirstLineOfCodeBlock(range, codeBlock)) {
                console.log('光标在代码块第一行，按上箭头');
                e.preventDefault();
                this.exitCodeBlockBefore(codeBlock, range);
            }
        }
    }
    
    isAtEndOfElement(range, element) {
        const endContainer = range.endContainer;
        const endOffset = range.endOffset;
        
        // 如果光标在元素的最后一个文本节点
        if (endContainer.nodeType === Node.TEXT_NODE) {
            return endContainer === element.lastChild && endOffset === endContainer.textContent.length;
        }
        
        // 如果光标在元素的最后一个子元素之后
        if (endContainer.nodeType === Node.ELEMENT_NODE) {
            return endContainer === element && endOffset === element.childNodes.length;
        }
        
        return false;
    }
    
    isAtStartOfElement(range, element) {
        const startContainer = range.startContainer;
        const startOffset = range.startOffset;
        
        // 如果光标在元素的第一个文本节点
        if (startContainer.nodeType === Node.TEXT_NODE) {
            return startContainer === element.firstChild && startOffset === 0;
        }
        
        // 如果光标在元素的第一个子元素之前
        if (startContainer.nodeType === Node.ELEMENT_NODE) {
            return startContainer === element && startOffset === 0;
        }
        
        return false;
    }
    
    isAtLastLineOfCodeBlock(range, codeBlock) {
        const endContainer = range.endContainer;
        const endOffset = range.endOffset;
        
        // 检查是否在代码块的最后一个文本节点
        if (endContainer.nodeType === Node.TEXT_NODE) {
            const textContent = endContainer.textContent;
            const lastNewlineIndex = textContent.lastIndexOf('\n');
            
            // 如果光标在最后一个换行符之后，或者没有换行符且光标在末尾
            if (lastNewlineIndex === -1) {
                return endOffset === textContent.length;
            } else {
                return endOffset > lastNewlineIndex;
            }
        }
        
        return false;
    }
    
    isAtFirstLineOfCodeBlock(range, codeBlock) {
        const startContainer = range.startContainer;
        const startOffset = range.startOffset;
        
        // 检查是否在代码块的第一个文本节点
        if (startContainer.nodeType === Node.TEXT_NODE) {
            const textContent = startContainer.textContent;
            const firstNewlineIndex = textContent.indexOf('\n');
            
            // 如果光标在第一个换行符之前，或者没有换行符且光标在开头
            if (firstNewlineIndex === -1) {
                return startOffset === 0;
            } else {
                return startOffset <= firstNewlineIndex;
            }
        }
        
        return false;
    }
    
    exitInlineCodeAfter(inlineCode, range) {
        console.log('退出行内代码（向后）');
        
        // 在行内代码后面插入一个文本节点
        const textNode = document.createTextNode('');
        inlineCode.parentNode.insertBefore(textNode, inlineCode.nextSibling);
        
        // 将光标移动到新插入的文本节点
        range.setStart(textNode, 0);
        range.setEnd(textNode, 0);
        
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        
        // 触发内容变化
        if (this.onContentChange) {
            this.onContentChange(this.getContent());
        }
    }
    
    exitInlineCodeBefore(inlineCode, range) {
        console.log('退出行内代码（向前）');
        
        // 在行内代码前面插入一个文本节点
        const textNode = document.createTextNode('');
        inlineCode.parentNode.insertBefore(textNode, inlineCode);
        
        // 将光标移动到新插入的文本节点
        range.setStart(textNode, 0);
        range.setEnd(textNode, 0);
        
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        
        // 触发内容变化
        if (this.onContentChange) {
            this.onContentChange(this.getContent());
        }
    }
    
    exitCodeBlockAfter(codeBlock, range) {
        console.log('退出代码块（向后）');
        
        // 在代码块后面插入一个段落
        const paragraph = document.createElement('p');
        const br = document.createElement('br');
        paragraph.appendChild(br);
        
        codeBlock.parentNode.insertBefore(paragraph, codeBlock.nextSibling);
        
        // 将光标移动到新插入的段落
        range.setStart(paragraph, 0);
        range.setEnd(paragraph, 0);
        
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        
        // 触发内容变化
        if (this.onContentChange) {
            this.onContentChange(this.getContent());
        }
    }
    
    exitCodeBlockBefore(codeBlock, range) {
        console.log('退出代码块（向前）');
        
        // 在代码块前面插入一个段落
        const paragraph = document.createElement('p');
        const br = document.createElement('br');
        paragraph.appendChild(br);
        
        codeBlock.parentNode.insertBefore(paragraph, codeBlock);
        
        // 将光标移动到新插入的段落
        range.setStart(paragraph, 0);
        range.setEnd(paragraph, 0);
        
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        
        // 触发内容变化
        if (this.onContentChange) {
            this.onContentChange(this.getContent());
        }
    }

    setLink() {
        console.log('setLink 被调用');
        
        this.content.focus();
        const selection = window.getSelection();
        
        console.log('选择范围数量:', selection.rangeCount);
        
        if (selection.rangeCount === 0) {
            console.log('没有选择范围');
            alert('请先选中要设置为链接的文字');
            return;
        }
        
        const range = selection.getRangeAt(0);
        const selectedText = range.toString();
        
        console.log('选中的文本:', selectedText);
        
        if (!selectedText) {
            console.log('选中的文本为空');
            alert('请先选中要设置为链接的文字');
            return;
        }
        
        // 保存选中的范围
        this.savedRange = range.cloneRange();
        console.log('已保存选中范围');
        
        console.log('显示链接模态框');
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
            // 聚焦到第一个输入框
            const textInput = modal.querySelector('#link-text');
            if (textInput) {
                textInput.focus();
                textInput.select();
            }
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
        console.log('insertLink 被调用:', { text, url });
        
        if (!this.savedRange) {
            console.error('没有保存的选中范围');
            alert('请先选中要设置为链接的文字');
            return;
        }
        
        console.log('使用保存的范围:', this.savedRange.toString());
        
        // 创建链接元素
        const linkElement = document.createElement('a');
        linkElement.href = url;
        linkElement.textContent = text;
        linkElement.target = '_blank';
        linkElement.rel = 'noopener noreferrer';
        linkElement.className = 'tiptap-link';
        
        console.log('创建的链接元素:', linkElement);
        
        try {
            // 使用保存的范围替换选中的文本
            this.savedRange.deleteContents();
            this.savedRange.insertNode(linkElement);
            
            // 选中新创建的链接
            const selection = window.getSelection();
            const newRange = document.createRange();
            newRange.selectNode(linkElement);
            selection.removeAllRanges();
            selection.addRange(newRange);
            
            console.log('链接插入成功');
            
            // 清除保存的范围
            this.savedRange = null;
            
            // 触发内容变化
            if (this.onContentChange) {
                this.onContentChange(this.getContent());
            }
        } catch (error) {
            console.error('插入链接时出错:', error);
            alert('插入链接失败，请重试');
        }
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
        try {
            // 获取HTML内容
            let htmlContent = this.content.innerHTML;
            
            // 调试日志
            console.log('SimpleTiptapEditor.getContent() - 原始内容:', htmlContent);
            
            // 确保内容不为undefined或null
            if (htmlContent === undefined || htmlContent === null) {
                console.log('SimpleTiptapEditor.getContent() - 内容为 undefined/null，设置为空字符串');
                htmlContent = '';
            }
            
            // 处理代码块，确保特殊字符被正确转义
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = htmlContent;
            
            // 处理所有代码块
            const codeElements = tempDiv.querySelectorAll('code');
            console.log('SimpleTiptapEditor.getContent() - 找到代码块数量:', codeElements.length);
            
            codeElements.forEach((codeElement, index) => {
                // 确保代码内容被正确转义
                const textContent = codeElement.textContent || codeElement.innerText || '';
                console.log(`SimpleTiptapEditor.getContent() - 代码块 ${index + 1} 原始内容:`, textContent);
                codeElement.innerHTML = this.escapeHtml(textContent);
                console.log(`SimpleTiptapEditor.getContent() - 代码块 ${index + 1} 转义后:`, codeElement.innerHTML);
            });
            
            const result = tempDiv.innerHTML;
            console.log('SimpleTiptapEditor.getContent() - 最终结果:', result);
            return result;
        } catch (error) {
            console.error('SimpleTiptapEditor.getContent() - 错误:', error);
            return '';
        }
    }
    
    // HTML转义函数
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    setContent(content) {
        // 确保内容不为undefined或null
        if (content === undefined || content === null) {
            content = '';
        }
        
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
                
                // 将光标移动到代码元素内部
                range.setStart(codeElement, codeElement.textContent.length);
                range.setEnd(codeElement, codeElement.textContent.length);
                selection.removeAllRanges();
                selection.addRange(range);
            } else {
                // 如果没有选中文本，插入代码标签
                const codeElement = document.createElement('code');
                codeElement.textContent = '代码';
                range.insertNode(codeElement);
                
                // 将光标移动到代码元素内部
                range.setStart(codeElement, codeElement.textContent.length);
                range.setEnd(codeElement, codeElement.textContent.length);
                selection.removeAllRanges();
                selection.addRange(range);
            }
        }
        if (this.onContentChange) {
            this.onContentChange(this.getContent());
        }
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
        if (this.onContentChange) {
            this.onContentChange(this.getContent());
        }
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
        if (this.onContentChange) {
            this.onContentChange(this.getContent());
        }
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
    



    destroy() {
        // 清理事件监听器
        if (this.content) {
            this.content.removeEventListener('input', this.updateToolbarState);
            this.content.removeEventListener('focus', this.updateToolbarState);
        }
    }
    
    // 插入图片功能
    insertImage() {
        this.content.focus();
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            
            // 创建图片上传模块
            const imageUploadModule = document.createElement('div');
            imageUploadModule.className = 'image-upload-module';
            imageUploadModule.innerHTML = `
                <div class="image-upload-container">
                    <div class="image-upload-area" id="image-upload-area">
                        <div class="upload-placeholder">
                            <i class="fas fa-cloud-upload-alt fa-3x"></i>
                            <p>点击或拖拽上传图片</p>
                            <p class="upload-hint">支持 JPG、PNG、GIF、WebP 格式，最大 5MB</p>
                        </div>
                        <input type="file" id="image-upload-input" accept="image/*" style="display: none;">
                    </div>
                    <div class="image-url-input">
                        <label>或者输入图片URL：</label>
                        <input type="url" id="image-url-input" placeholder="https://example.com/image.jpg">
                        <button type="button" id="insert-url-btn">插入URL</button>
                    </div>
                    <div class="image-upload-actions">
                        <button type="button" id="cancel-upload-btn">取消</button>
                    </div>
                </div>
            `;
            
            range.deleteContents();
            range.insertNode(imageUploadModule);
            
            // 绑定事件
            this.bindImageUploadEvents(imageUploadModule, range);
            
            // 将光标移到上传模块后面
            range.setStartAfter(imageUploadModule);
            range.collapse(true);
            selection.removeAllRanges();
            selection.addRange(range);
        }
    }
    
    // 绑定图片上传事件
    bindImageUploadEvents(uploadModule, range) {
        const uploadArea = uploadModule.querySelector('#image-upload-area');
        const uploadInput = uploadModule.querySelector('#image-upload-input');
        const urlInput = uploadModule.querySelector('#image-url-input');
        const insertUrlBtn = uploadModule.querySelector('#insert-url-btn');
        const cancelBtn = uploadModule.querySelector('#cancel-upload-btn');
        
        // 点击上传区域
        uploadArea.addEventListener('click', () => {
            uploadInput.click();
        });
        
        // 文件选择
        uploadInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.uploadImageFile(file, uploadModule, range);
            }
        });
        
        // 拖拽上传
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = 'rgba(59, 130, 246, 0.5)';
            uploadArea.style.backgroundColor = 'rgba(59, 130, 246, 0.1)';
        });
        
        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = 'rgba(255, 255, 255, 0.3)';
            uploadArea.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = 'rgba(255, 255, 255, 0.3)';
            uploadArea.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.uploadImageFile(files[0], uploadModule, range);
            }
        });
        
        // URL输入
        insertUrlBtn.addEventListener('click', () => {
            const url = urlInput.value.trim();
            if (url) {
                this.insertImageFromUrl(url, uploadModule, range);
            }
        });
        
        // 取消上传
        cancelBtn.addEventListener('click', () => {
            uploadModule.remove();
            if (this.onContentChange) {
                this.onContentChange(this.getContent());
            }
        });
    }
    
    // 上传图片文件
    uploadImageFile(file, uploadModule, range) {
        // 检查文件类型
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
        if (!allowedTypes.includes(file.type)) {
            alert('请选择图片文件（JPG、PNG、GIF、WebP）');
            return;
        }
        
        // 检查文件大小（5MB）
        if (file.size > 5 * 1024 * 1024) {
            alert('图片大小不能超过5MB');
            return;
        }
        
        // 显示上传进度
        const uploadArea = uploadModule.querySelector('#image-upload-area');
        uploadArea.innerHTML = '<i class="fas fa-spinner fa-spin fa-2x"></i><p>上传中...</p>';
        
        // 创建FormData
        const formData = new FormData();
        formData.append('image', file);
        
        // 上传图片
        fetch('/api/upload-image', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.insertImageFromUrl(data.url, uploadModule, range);
            } else {
                alert('上传失败：' + data.message);
                this.resetUploadArea(uploadModule);
            }
        })
        .catch(error => {
            console.error('上传错误:', error);
            alert('上传失败，请稍后重试');
            this.resetUploadArea(uploadModule);
        });
    }
    
    // 从URL插入图片
    insertImageFromUrl(url, uploadModule, range) {
        const img = document.createElement('img');
        img.src = url;
        img.alt = '插入的图片';
        img.style.maxWidth = '100%';
        img.style.height = 'auto';
        img.style.borderRadius = '8px';
        img.style.margin = '10px 0';
        
        // 替换上传模块
        uploadModule.parentNode.replaceChild(img, uploadModule);
        
        // 将光标移到图片后面
        const newRange = document.createRange();
        newRange.setStartAfter(img);
        newRange.collapse(true);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(newRange);
        
        if (this.onContentChange) {
            this.onContentChange(this.getContent());
        }
    }
    
    // 重置上传区域
    resetUploadArea(uploadModule) {
        const uploadArea = uploadModule.querySelector('#image-upload-area');
        uploadArea.innerHTML = `
            <div class="upload-placeholder">
                <i class="fas fa-cloud-upload-alt fa-3x"></i>
                <p>点击或拖拽上传图片</p>
                <p class="upload-hint">支持 JPG、PNG、GIF、WebP 格式，最大 5MB</p>
            </div>
            <input type="file" id="image-upload-input" accept="image/*" style="display: none;">
        `;
        
        // 重新绑定事件
        const uploadInput = uploadArea.querySelector('#image-upload-input');
        uploadInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.uploadImageFile(file, uploadModule, range);
            }
        });
    }
    
    // 插入表格功能
    insertTable() {
        this.content.focus();
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            
            // 创建表格
            const table = document.createElement('table');
            table.className = 'tiptap-table';
            table.style.borderCollapse = 'collapse';
            table.style.width = '100%';
            table.style.margin = '10px 0';
            table.style.border = '1px solid rgba(255, 255, 255, 0.2)';
            
            // 创建表头
            const thead = document.createElement('thead');
            const headerRow = document.createElement('tr');
            for (let i = 0; i < 3; i++) {
                const th = document.createElement('th');
                th.textContent = `标题 ${i + 1}`;
                th.style.border = '1px solid rgba(255, 255, 255, 0.2)';
                th.style.padding = '8px 12px';
                th.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
                th.style.textAlign = 'left';
                headerRow.appendChild(th);
            }
            thead.appendChild(headerRow);
            table.appendChild(thead);
            
            // 创建表体
            const tbody = document.createElement('tbody');
            for (let i = 0; i < 2; i++) {
                const row = document.createElement('tr');
                for (let j = 0; j < 3; j++) {
                    const td = document.createElement('td');
                    td.textContent = `内容 ${i + 1}-${j + 1}`;
                    td.style.border = '1px solid rgba(255, 255, 255, 0.2)';
                    td.style.padding = '8px 12px';
                    row.appendChild(td);
                }
                tbody.appendChild(row);
            }
            table.appendChild(tbody);
            
            range.deleteContents();
            range.insertNode(table);
            
            // 将光标移到表格后面
            range.setStartAfter(table);
            range.collapse(true);
            selection.removeAllRanges();
            selection.addRange(range);
        }
        
        if (this.onContentChange) {
            this.onContentChange(this.getContent());
        }
    }
    
    // 添加表格行
    addTableRow() {
        const table = this.getCurrentTable();
        if (table) {
            const tbody = table.querySelector('tbody') || table;
            const rowCount = tbody.rows.length;
            const colCount = tbody.rows[0] ? tbody.rows[0].cells.length : 3;
            
            const newRow = document.createElement('tr');
            for (let i = 0; i < colCount; i++) {
                const td = document.createElement('td');
                td.textContent = `新内容 ${rowCount + 1}-${i + 1}`;
                td.style.border = '1px solid rgba(255, 255, 255, 0.2)';
                td.style.padding = '8px 12px';
                newRow.appendChild(td);
            }
            tbody.appendChild(newRow);
            
            if (this.onContentChange) {
                this.onContentChange(this.getContent());
            }
        }
    }
    
    // 添加表格列
    addTableColumn() {
        const table = this.getCurrentTable();
        if (table) {
            const rows = table.querySelectorAll('tr');
            const colCount = rows[0] ? rows[0].cells.length : 0;
            
            rows.forEach((row, index) => {
                const cell = document.createElement(index === 0 ? 'th' : 'td');
                cell.textContent = index === 0 ? `标题 ${colCount + 1}` : `内容 ${index}-${colCount + 1}`;
                cell.style.border = '1px solid rgba(255, 255, 255, 0.2)';
                cell.style.padding = '8px 12px';
                if (index === 0) {
                    cell.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
                }
                row.appendChild(cell);
            });
            
            if (this.onContentChange) {
                this.onContentChange(this.getContent());
            }
        }
    }
    
    // 删除表格行
    deleteTableRow() {
        const table = this.getCurrentTable();
        if (table) {
            const tbody = table.querySelector('tbody') || table;
            const rows = tbody.querySelectorAll('tr');
            if (rows.length > 1) {
                const lastRow = rows[rows.length - 1];
                lastRow.remove();
                
                if (this.onContentChange) {
                    this.onContentChange(this.getContent());
                }
            }
        }
    }
    
    // 删除表格列
    deleteTableColumn() {
        const table = this.getCurrentTable();
        if (table) {
            const rows = table.querySelectorAll('tr');
            if (rows.length > 0 && rows[0].cells.length > 1) {
                rows.forEach(row => {
                    const lastCell = row.cells[row.cells.length - 1];
                    lastCell.remove();
                });
                
                if (this.onContentChange) {
                    this.onContentChange(this.getContent());
                }
            }
        }
    }
    
    // 获取当前光标所在的表格
    getCurrentTable() {
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            let container = range.commonAncestorContainer;
            
            // 如果容器是文本节点，获取其父元素
            if (container.nodeType === Node.TEXT_NODE) {
                container = container.parentNode;
            }
            
            // 向上查找表格元素
            while (container && container !== this.content) {
                if (container.tagName === 'TABLE') {
                    return container;
                }
                container = container.parentNode;
            }
        }
        return null;
    }
}

// 导出类
window.SimpleTiptapEditor = SimpleTiptapEditor;
