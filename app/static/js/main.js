// 主要的JavaScript功能

// 全局消息提示函数
function showMessage(message, type = 'info', duration = 3000) {
    // 创建消息容器（如果不存在）
    let messageContainer = document.getElementById('message-container');
    if (!messageContainer) {
        messageContainer = document.createElement('div');
        messageContainer.id = 'message-container';
        messageContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            max-width: 400px;
        `;
        document.body.appendChild(messageContainer);
    }

    // 创建消息元素
    const messageEl = document.createElement('div');
    messageEl.className = `message-toast message-${type}`;
    messageEl.style.cssText = `
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 1rem 1.5rem;
        margin-bottom: 0.5rem;
        box-shadow: var(--shadow-lg);
        display: flex;
        align-items: center;
        gap: 0.75rem;
        animation: slideInRight 0.3s ease-out;
        position: relative;
        min-width: 300px;
    `;

    // 根据类型设置图标和颜色
    let icon, color;
    switch (type) {
        case 'success':
            icon = 'fas fa-check-circle';
            color = '#10b981';
            break;
        case 'error':
            icon = 'fas fa-exclamation-circle';
            color = '#ef4444';
            break;
        case 'warning':
            icon = 'fas fa-exclamation-triangle';
            color = '#f59e0b';
            break;
        case 'info':
        default:
            icon = 'fas fa-info-circle';
            color = '#3b82f6';
            break;
    }

    messageEl.innerHTML = `
        <i class="${icon}" style="color: ${color}; font-size: 1.25rem;"></i>
        <span style="color: var(--text-primary); flex: 1;">${message}</span>
        <button class="message-close" style="
            background: none;
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            padding: 0.25rem;
            border-radius: var(--border-radius);
            transition: all 0.2s ease;
        ">
            <i class="fas fa-times"></i>
        </button>
    `;

    // 添加关闭按钮事件
    const closeBtn = messageEl.querySelector('.message-close');
    closeBtn.addEventListener('click', () => {
        messageEl.style.animation = 'slideOutRight 0.3s ease-in';
        setTimeout(() => {
            if (messageEl.parentNode) {
                messageEl.remove();
            }
        }, 300);
    });

    // 添加到容器
    messageContainer.appendChild(messageEl);

    // 自动关闭
    if (duration > 0) {
        setTimeout(() => {
            if (messageEl.parentNode) {
                messageEl.style.animation = 'slideOutRight 0.3s ease-in';
                setTimeout(() => {
                    if (messageEl.parentNode) {
                        messageEl.remove();
                    }
                }, 300);
            }
        }, duration);
    }

    return messageEl;
}

// 添加CSS动画
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100%);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideOutRight {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100%);
        }
    }
    
    .message-close:hover {
        background: var(--bg-hover) !important;
        color: var(--text-primary) !important;
    }
`;
document.head.appendChild(style);

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
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
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

    // 项目筛选功能
    const filterButtons = document.querySelectorAll('[data-filter]');
    const projectItems = document.querySelectorAll('.project-item');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const filter = this.getAttribute('data-filter');
            
            // 更新按钮状态
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // 筛选项目
            projectItems.forEach(item => {
                if (filter === 'all' || item.getAttribute('data-category') === filter) {
                    item.style.display = 'block';
                    item.classList.add('fade-in-up');
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });

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
        if (window.scrollY > 300) {
            backToTopBtn.style.display = 'block';
        } else {
            backToTopBtn.style.display = 'none';
        }
    });

    // 返回顶部功能
    backToTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // 消息提示功能
    window.showAlert = function(message, type = 'info') {
        try {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
            alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            document.body.appendChild(alertDiv);
            
            // 自动移除
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.remove();
                }
            }, 3000);
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
            { title: 'Flask项目实战', type: '项目', url: '/projects/flask-project' },
            { title: 'JavaScript基础', type: '文章', url: '/blog/javascript-basics' },
            { title: 'React组件开发', type: '项目', url: '/projects/react-components' },
            { title: 'Docker容器化部署', type: '文章', url: '/blog/docker-deployment' },
            { title: 'Vue.js前端框架', type: '项目', url: '/projects/vue-framework' },
            { title: 'MySQL数据库优化', type: '文章', url: '/blog/mysql-optimization' },
            { title: '微服务架构设计', type: '项目', url: '/projects/microservices' }
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
            if (homeSearchInput) {
                homeSearchInput.focus();
            } else if (globalSearchInput) {
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
                const perfData = performance.getEntriesByType('navigation')[0];
                console.log('页面加载时间:', perfData.loadEventEnd - perfData.loadEventStart, 'ms');
            }, 0);
        });
    }
});

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
    showAlert: window.showAlert
}; 