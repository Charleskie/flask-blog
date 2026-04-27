// 主要的JavaScript功能

function getToastIconClass(type) {
    switch (type) {
        case 'success':
            return 'fa-check';
        case 'error':
            return 'fa-circle-exclamation';
        case 'warning':
            return 'fa-triangle-exclamation';
        case 'info':
        default:
            return 'fa-info';
    }
}

function getDialogIconClass(type) {
    switch (type) {
        case 'success':
            return 'fa-check';
        case 'error':
            return 'fa-trash';
        case 'warning':
            return 'fa-triangle-exclamation';
        case 'info':
        default:
            return 'fa-bell';
    }
}

function ensureToastContainer() {
    let container = document.getElementById('site-toast-stack');
    if (!container) {
        container = document.createElement('div');
        container.id = 'site-toast-stack';
        container.className = 'site-toast-stack';
        container.setAttribute('aria-live', 'polite');
        container.setAttribute('aria-atomic', 'false');
        document.body.appendChild(container);
    }
    return container;
}

function releaseDialogLock() {
    if (!document.querySelector('.site-dialog-backdrop, #loginModal.d-flex, .site-confirm-overlay.d-flex')) {
        document.body.classList.remove('has-site-dialog');
    }
}

function showToast(message, type = 'info', duration = 3000) {
    const container = ensureToastContainer();
    const toast = document.createElement('div');
    toast.className = `message-toast ${type}`;
    toast.innerHTML = `
        <span class="message-toast-icon" aria-hidden="true">
            <i class="fas ${getToastIconClass(type)}"></i>
        </span>
        <div class="message-toast-content">
            <div class="message-toast-message"></div>
        </div>
        <button type="button" class="message-toast-close" aria-label="关闭提醒">
            <i class="fas fa-times"></i>
        </button>
    `;

    const messageNode = toast.querySelector('.message-toast-message');
    messageNode.textContent = String(message ?? '');

    const closeToast = () => {
        if (!toast.parentNode) {
            return;
        }
        toast.classList.add('hide');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 220);
    };

    toast.querySelector('.message-toast-close').addEventListener('click', closeToast);
    container.appendChild(toast);

    if (duration > 0) {
        setTimeout(closeToast, duration);
    }

    return toast;
}

function buildDialog(options = {}) {
    const {
        title = '提示',
        message = '',
        type = 'info',
        confirmText = '知道了',
        cancelText = '取消',
        showCancel = false,
        danger = false
    } = options;

    return new Promise((resolve) => {
        const overlay = document.createElement('div');
        overlay.className = 'site-dialog-backdrop';

        const panel = document.createElement('div');
        panel.className = 'site-dialog-panel';
        panel.setAttribute('role', 'dialog');
        panel.setAttribute('aria-modal', 'true');

        const head = document.createElement('div');
        head.className = 'site-dialog-head';

        const headMain = document.createElement('div');
        headMain.className = 'site-dialog-head-main';

        const icon = document.createElement('span');
        icon.className = `site-dialog-icon ${danger ? 'error' : type}`;
        icon.setAttribute('aria-hidden', 'true');
        icon.innerHTML = `<i class="fas ${getDialogIconClass(danger ? 'error' : type)}"></i>`;

        const heading = document.createElement('h3');
        heading.className = 'site-dialog-title';
        heading.textContent = title;

        const closeButton = document.createElement('button');
        closeButton.type = 'button';
        closeButton.className = 'btn-close';
        closeButton.setAttribute('aria-label', '关闭');

        const body = document.createElement('div');
        body.className = 'site-dialog-body';

        const content = document.createElement('p');
        content.className = 'site-dialog-message';
        content.textContent = String(message ?? '');

        const actions = document.createElement('div');
        actions.className = 'site-dialog-actions';
        if (!showCancel) {
            actions.classList.add('site-dialog-actions-centered');
        }

        const confirmButton = document.createElement('button');
        confirmButton.type = 'button';
        confirmButton.className = danger ? 'btn btn-danger' : 'btn btn-primary';
        confirmButton.textContent = confirmText;

        let cancelButton = null;
        if (showCancel) {
            cancelButton = document.createElement('button');
            cancelButton.type = 'button';
            cancelButton.className = 'btn btn-secondary';
            cancelButton.textContent = cancelText;
            actions.appendChild(cancelButton);
        }
        actions.appendChild(confirmButton);

        headMain.append(icon, heading);
        head.append(headMain, closeButton);
        body.append(content, actions);
        panel.append(head, body);
        overlay.appendChild(panel);
        document.body.appendChild(overlay);
        document.body.classList.add('has-site-dialog');

        const cleanup = (result) => {
            document.removeEventListener('keydown', onKeyDown);
            overlay.remove();
            releaseDialogLock();
            resolve(result);
        };

        const onKeyDown = (event) => {
            if (event.key === 'Escape') {
                cleanup(false);
            }
        };

        document.addEventListener('keydown', onKeyDown);
        overlay.addEventListener('click', (event) => {
            if (event.target === overlay) {
                cleanup(false);
            }
        });
        closeButton.addEventListener('click', () => cleanup(false));
        if (cancelButton) {
            cancelButton.addEventListener('click', () => cleanup(false));
        }
        confirmButton.addEventListener('click', () => cleanup(true));
        confirmButton.focus();
    });
}

window.siteUI = window.siteUI || {};
window.siteUI.showToast = showToast;
window.siteUI.alert = function(message, options = {}) {
    return buildDialog({
        title: options.title || '提示',
        message,
        type: options.type || 'info',
        confirmText: options.confirmText || '知道了',
        danger: false,
        showCancel: false
    });
};
window.siteUI.confirm = function(message, options = {}) {
    return buildDialog({
        title: options.title || '确认操作',
        message,
        type: options.type || 'warning',
        confirmText: options.confirmText || '确认',
        cancelText: options.cancelText || '取消',
        danger: Boolean(options.danger),
        showCancel: true
    });
};

window.showToast = showToast;
window.showAlert = function(message, type = 'info') {
    return showToast(message, type);
};
window.confirmAsync = function(message, options = {}) {
    return window.siteUI.confirm(message, options);
};
window.alert = function(message) {
    return window.showToast(String(message ?? ''), 'warning', 3600);
};

function showMessage(message, type = 'info', duration = 3000) {
    return window.showToast(message, type, duration);
}

window.showMessage = showMessage;

// 处理表单提交和消息显示
function handleFormSubmit(form, options = {}) {
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn ? submitBtn.textContent : '';
        
        // 显示加载状态
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 处理中...';
        }
        
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                showMessage(result.message, 'success');
                
                // 如果有重定向URL，延迟跳转
                if (result.redirect) {
                    setTimeout(() => {
                        window.location.href = result.redirect;
                    }, 1500);
                } else if (options.onSuccess) {
                    options.onSuccess(result);
                }
            } else {
                showMessage(result.message, 'error');
                if (options.onError) {
                    options.onError(result);
                }
            }
        } catch (error) {
            console.error('表单提交错误:', error);
            showMessage('请求失败，请稍后重试', 'error');
        } finally {
            // 恢复按钮状态
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // 初始化工具提示
    try {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    } catch (error) {
        console.error('工具提示初始化错误:', error);
    }
    
    // 自动处理带有 data-ajax-form 属性的表单
    document.querySelectorAll('form[data-ajax-form]').forEach(form => {
        handleFormSubmit(form);
    });

    // 平滑滚动
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            // 检查href是否有效（不是只有#）
            if (href && href.length > 1) {
                const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                }
            }
        });
    });

    // 导航栏滚动效果
    window.addEventListener('scroll', function() {
        const navbar = safeQuerySelector('header');
        if (window.scrollY > 50) {
            safeClassListOperation(navbar, 'add', 'navbar-scrolled');
        } else {
            safeClassListOperation(navbar, 'remove', 'navbar-scrolled');
        }
    });

    // 技能进度条动画
    function animateProgressBars() {
        const progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach(bar => {
            const width = bar.style.width;
            bar.style.width = '0%';
            setTimeout(() => {
                bar.style.width = width;
            }, 500);
        });
    }

    // 当技能区域进入视口时触发动画
    const skillsSection = document.querySelector('.skill-item');
    if (skillsSection) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateProgressBars();
                    observer.unobserve(entry.target);
                }
            });
        });
        observer.observe(skillsSection);
    }

    // 表单验证
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // 联系表单处理
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // 显示加载状态
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="loading"></span> 发送中...';
            submitBtn.disabled = true;
            
            // 模拟发送过程
            setTimeout(() => {
                // 显示成功消息
                showAlert('消息已发送！我会尽快回复您。', 'success');
                
                // 重置表单
                contactForm.reset();
                
                // 恢复按钮状态
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }, 2000);
        });
    }

    // 搜索功能
    const searchInput = document.querySelector('input[placeholder*="搜索"]');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const articles = document.querySelectorAll('article');
            
            articles.forEach(article => {
                const title = article.querySelector('.card-title').textContent.toLowerCase();
                const content = article.querySelector('.card-text').textContent.toLowerCase();
                
                if (title.includes(searchTerm) || content.includes(searchTerm)) {
                    article.style.display = 'block';
                } else {
                    article.style.display = 'none';
                }
            });
        });
    }

    // 返回顶部按钮
    const backToTopBtn = document.createElement('button');
    backToTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    backToTopBtn.className = 'btn btn-primary position-fixed';
    backToTopBtn.style.cssText = 'bottom: 20px; right: 20px; z-index: 1000; border-radius: 50%; width: 50px; height: 50px; display: none;';
    document.body.appendChild(backToTopBtn);

    // 显示/隐藏返回顶部按钮
    window.addEventListener('scroll', function() {
        try {
            if (backToTopBtn && backToTopBtn.style) {
                if (window.scrollY > 300) {
                    backToTopBtn.style.display = 'block';
                } else {
                    backToTopBtn.style.display = 'none';
                }
            }
        } catch (error) {
            console.error('返回顶部按钮滚动效果错误:', error);
        }
    });

    // 返回顶部功能
    backToTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // 消息提示功能使用共享提醒组件
    window.showAlert = function(message, type = 'info') {
        try {
            return showMessage(message, type);
        } catch (error) {
            console.error('showAlert函数错误:', error);
        }
    };

    // 图片懒加载
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));

    // 主题切换功能
    const themeOptionItems = document.querySelectorAll('.theme-option-item');
    const savedTheme = localStorage.getItem('theme') || 'dark';
    
    // 应用主题
    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        // 更新主题选项的激活状态
        themeOptionItems.forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('data-theme') === theme) {
                item.classList.add('active');
            }
        });
    }
    
    // 初始化主题
    applyTheme(savedTheme);
    
    // 主题切换事件
    themeOptionItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const theme = this.getAttribute('data-theme');
            applyTheme(theme);
            
            // 关闭下拉菜单
            const dropdown = bootstrap.Dropdown.getInstance(document.getElementById('themeDropdown'));
            if (dropdown) {
                dropdown.hide();
            }
        });
    });

    // 全局搜索功能
    const globalSearchInput = document.getElementById('globalSearchInput');
    const searchSuggestions = document.getElementById('searchSuggestions');
    const homeSearchInput = document.getElementById('homeSearchInput');
    const homeSearchSuggestions = document.getElementById('homeSearchSuggestions');
    let searchTimeout;

    if (globalSearchInput && searchSuggestions) {
        // 搜索建议功能
        globalSearchInput.addEventListener('input', function() {
            const query = this.value.trim();
            
            clearTimeout(searchTimeout);
            
            if (query.length < 2) {
                searchSuggestions.style.display = 'none';
                return;
            }
            
            searchTimeout = setTimeout(() => {
                fetchSearchSuggestions(query);
            }, 300);
        });

        // 点击外部关闭建议
        document.addEventListener('click', function(e) {
            if (!globalSearchInput.contains(e.target) && !searchSuggestions.contains(e.target)) {
                searchSuggestions.style.display = 'none';
            }
        });

        // 键盘导航
        globalSearchInput.addEventListener('keydown', function(e) {
            const suggestions = searchSuggestions.querySelectorAll('.search-suggestion');
            const activeSuggestion = searchSuggestions.querySelector('.search-suggestion.active');
            
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                if (activeSuggestion) {
                    activeSuggestion.classList.remove('active');
                    const next = activeSuggestion.nextElementSibling;
                    if (next) {
                        next.classList.add('active');
                    } else {
                        suggestions[0]?.classList.add('active');
                    }
                } else {
                    suggestions[0]?.classList.add('active');
                }
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                if (activeSuggestion) {
                    activeSuggestion.classList.remove('active');
                    const prev = activeSuggestion.previousElementSibling;
                    if (prev) {
                        prev.classList.add('active');
                    } else {
                        suggestions[suggestions.length - 1]?.classList.add('active');
                    }
                } else {
                    suggestions[suggestions.length - 1]?.classList.add('active');
                }
            } else if (e.key === 'Enter') {
                e.preventDefault();
                if (activeSuggestion) {
                    const link = activeSuggestion.querySelector('a');
                    if (link) {
                        window.location.href = link.href;
                    }
                } else {
                    // 执行搜索
                    const form = globalSearchInput.closest('form');
                    if (form) {
                        form.submit();
                    }
                }
            } else if (e.key === 'Escape') {
                searchSuggestions.style.display = 'none';
                globalSearchInput.blur();
            }
        });
    }

    // 首页搜索功能
    if (homeSearchInput && homeSearchSuggestions) {
        homeSearchInput.addEventListener('input', function() {
            const query = this.value.trim();
            
            clearTimeout(searchTimeout);
            
            if (query.length < 2) {
                homeSearchSuggestions.style.display = 'none';
                return;
            }
            
            searchTimeout = setTimeout(() => {
                fetchSearchSuggestions(query, homeSearchSuggestions);
            }, 300);
        });

        // 点击外部关闭建议
        document.addEventListener('click', function(e) {
            if (!homeSearchInput.contains(e.target) && !homeSearchSuggestions.contains(e.target)) {
                homeSearchSuggestions.style.display = 'none';
            }
        });

        // 键盘导航
        homeSearchInput.addEventListener('keydown', function(e) {
            const suggestions = homeSearchSuggestions.querySelectorAll('.search-suggestion');
            const activeSuggestion = homeSearchSuggestions.querySelector('.search-suggestion.active');
            
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                if (activeSuggestion) {
                    activeSuggestion.classList.remove('active');
                    const next = activeSuggestion.nextElementSibling;
                    if (next) {
                        next.classList.add('active');
                    } else {
                        suggestions[0]?.classList.add('active');
                    }
                } else {
                    suggestions[0]?.classList.add('active');
                }
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                if (activeSuggestion) {
                    activeSuggestion.classList.remove('active');
                    const prev = activeSuggestion.previousElementSibling;
                    if (prev) {
                        prev.classList.add('active');
                    } else {
                        suggestions[suggestions.length - 1]?.classList.add('active');
                    }
                } else {
                    suggestions[suggestions.length - 1]?.classList.add('active');
                }
            } else if (e.key === 'Enter') {
                e.preventDefault();
                if (activeSuggestion) {
                    const link = activeSuggestion.querySelector('a');
                    if (link) {
                        window.location.href = link.href;
                    }
                } else {
                    // 执行搜索
                    const form = homeSearchInput.closest('form');
                    if (form) {
                        form.submit();
                    }
                }
            } else if (e.key === 'Escape') {
                homeSearchSuggestions.style.display = 'none';
                homeSearchInput.blur();
            }
        });
    }

    // 获取搜索建议
    function fetchSearchSuggestions(query, targetElement = searchSuggestions) {
        // 这里可以调用后端API获取搜索建议
        // 现在使用模拟数据
        const mockSuggestions = [
            { title: 'Python开发教程', type: '文章', url: '/blog/python-tutorial' },
            { title: 'JavaScript基础', type: '文章', url: '/blog/javascript-basics' },
            { title: 'Docker容器化部署', type: '文章', url: '/blog/docker-deployment' },
            { title: 'MySQL数据库优化', type: '文章', url: '/blog/mysql-optimization' }
        ];

        const filteredSuggestions = mockSuggestions.filter(item => 
            item.title.toLowerCase().includes(query.toLowerCase())
        );

        displaySearchSuggestions(filteredSuggestions, targetElement);
    }

    // 显示搜索建议
    function displaySearchSuggestions(suggestions, targetElement) {
        if (suggestions.length === 0) {
            targetElement.style.display = 'none';
            return;
        }

        targetElement.innerHTML = suggestions.map(suggestion => `
            <div class="search-suggestion">
                <a href="${suggestion.url}" class="text-decoration-none">
                    <div class="suggestion-title">${suggestion.title}</div>
                    <div class="suggestion-type">${suggestion.type}</div>
                </a>
            </div>
        `).join('');

        targetElement.style.display = 'block';

        // 添加点击事件
        targetElement.querySelectorAll('.search-suggestion').forEach((suggestion, index) => {
            suggestion.addEventListener('mouseenter', function() {
                targetElement.querySelectorAll('.search-suggestion').forEach(s => s.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }

    // 键盘快捷键
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K 打开搜索
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            if (homeSearchInput && homeSearchInput.focus) {
                homeSearchInput.focus();
            } else if (globalSearchInput && globalSearchInput.focus) {
                globalSearchInput.focus();
            }
        }
        
        // ESC 关闭模态框
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(modal => {
                const modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            });
        }
    });

    // 页面加载动画
    window.addEventListener('load', function() {
        document.body.classList.add('loaded');
    });

    // 错误处理
    window.addEventListener('error', function(e) {
        console.error('JavaScript错误:', e.error);
        // 只在控制台记录错误，不显示弹窗
        return false;
    });

    // 性能监控
    if ('performance' in window) {
        window.addEventListener('load', function() {
            setTimeout(() => {
                const perfData = performance.getEntriesByType('navigation')[0];}, 0);
        });
    }
});

// 全局classList操作保护函数
function safeClassListOperation(element, operation, ...classes) {
    try {
        if (element && element.classList && typeof element.classList[operation] === 'function') {
            element.classList[operation](...classes);
            return true;
        }
    } catch (error) {
        console.error(`classList ${operation} 操作失败:`, error);
    }
    return false;
}

// 全局元素查找保护函数
function safeQuerySelector(selector) {
    try {
        return document.querySelector(selector);
    } catch (error) {
        console.error(`查找元素失败 (${selector}):`, error);
        return null;
    }
}

// 工具函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 导出函数供其他模块使用
window.utils = {
    debounce,
    throttle,
    showToast: window.showToast,
    showAlert: window.showAlert,
    confirmAsync: window.confirmAsync,
    safeClassListOperation,
    safeQuerySelector
};
