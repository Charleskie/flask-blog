/**
 * 交互功能JavaScript
 * 处理点赞、收藏、评论等功能
 */

class InteractionManager {
    constructor() {
        this.init();
    }

    init() {
        this.currentUser = null;
        this.isAdmin = false;
        this.tempRating = null; // 暂存评分
        this.loadCurrentUser();
        this.bindEvents();
        this.loadUserStatus();
        this.loadComments();
    }

    async loadCurrentUser() {
        try {
            const response = await fetch('/api/user-info');
            if (response.ok) {
                const result = await response.json();
                this.currentUser = result.user;
                this.isAdmin = result.user && result.user.is_admin;
            } else if (response.status === 401) {
                // 检查当前页面是否是登录或注册页面
                const currentPath = window.location.pathname;
                const isAuthPage = currentPath.includes('/login') || currentPath.includes('/register');
                
                console.log('当前路径:', currentPath);
                console.log('是否为认证页面:', isAuthPage);
                
                // 只有在非登录/注册页面才显示登录提示
                if (!isAuthPage) {
                    console.log('显示登录提示弹窗');
                    this.showLoginPrompt();
                } else {
                    console.log('跳过登录提示（认证页面）');
                }
            }
        } catch (error) {
            console.log('获取用户信息失败:', error);
        }
    }

    showLoginPrompt() {
        console.log('开始创建登录提示弹窗');
        // 使用和showMessage一致的样式创建登录提示
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
        messageEl.className = 'message-toast message-warning';
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

        messageEl.innerHTML = `
            <i class="fas fa-sign-in-alt" style="color: #f59e0b; font-size: 1.25rem;"></i>
            <div style="color: var(--text-primary); flex: 1;">
                <div style="font-weight: 600; margin-bottom: 0.5rem;">需要登录</div>
                <div style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.75rem;">您需要登录才能使用此功能</div>
                <div style="display: flex; gap: 0.5rem;">
                    <button class="login-btn" style="
                        background: var(--primary-color);
                        color: white;
                        border: none;
                        padding: 0.5rem 1rem;
                        border-radius: var(--border-radius);
                        font-size: 0.875rem;
                        cursor: pointer;
                        transition: all 0.2s ease;
                    ">
                        <i class="fas fa-sign-in-alt"></i> 登录
                    </button>
                    <button class="register-btn" style="
                        background: transparent;
                        color: var(--primary-color);
                        border: 1px solid var(--primary-color);
                        padding: 0.5rem 1rem;
                        border-radius: var(--border-radius);
                        font-size: 0.875rem;
                        cursor: pointer;
                        transition: all 0.2s ease;
                    ">
                        <i class="fas fa-user-plus"></i> 注册
                    </button>
                </div>
            </div>
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
        
        messageContainer.appendChild(messageEl);
        
        // 绑定事件
        const closeBtn = messageEl.querySelector('.message-close');
        const loginBtn = messageEl.querySelector('.login-btn');
        const registerBtn = messageEl.querySelector('.register-btn');
        
        closeBtn.addEventListener('click', () => {
            messageEl.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => {
                if (messageEl.parentNode) {
                    messageEl.remove();
                }
            }, 300);
        });
        
        loginBtn.addEventListener('click', () => {
            window.location.href = '/login';
        });
        
        registerBtn.addEventListener('click', () => {
            window.location.href = '/register';
        });
        
        // 5秒后自动关闭
        setTimeout(() => {
            if (messageEl.parentNode) {
                messageEl.style.animation = 'slideOutRight 0.3s ease-in';
                setTimeout(() => {
                    if (messageEl.parentNode) {
                        messageEl.remove();
                    }
                }, 300);
            }
        }, 5000);
    }

    bindEvents() {
        console.log('绑定事件监听器...');
        // 点赞按钮事件
        document.addEventListener('click', (e) => {
            console.log('点击事件触发:', e.target);
            
            if (e.target.closest('.like-btn')) {
                console.log('点赞按钮被点击');
                e.preventDefault();
                this.handleLike(e.target.closest('.like-btn'));
            }
            
            if (e.target.closest('.favorite-btn')) {
                console.log('收藏按钮被点击');
                e.preventDefault();
                this.handleFavorite(e.target.closest('.favorite-btn'));
            }
            
            if (e.target.closest('.comment-like-btn')) {
                console.log('评论点赞按钮被点击');
                e.preventDefault();
                this.handleCommentLike(e.target.closest('.comment-like-btn'));
            }
            
             // 评论提交按钮事件
            if (e.target.closest('.comment-submit')) {
                console.log('评论提交按钮被点击');
                e.preventDefault();
                const form = e.target.closest('.comment-form');
                if (form) {
                    this.handleComment(form);
                }
            }
        });

        // 评分选择事件 - 自动保存评分
        document.addEventListener('change', (e) => {
            if (e.target.name === 'rating' && (e.target.closest('.rating-section') || e.target.closest('.floating-rating-section'))) {
                console.log('评分被选择:', e.target.value);
                this.handleRatingChange(e.target);
            }
        });

        // 评分悬停事件（仅限互动统计模块）
        document.addEventListener('mouseover', (e) => {
            if (e.target.closest('.rating-section .rating-input label')) {
                this.handleRatingHover(e.target);
            }
        });

        document.addEventListener('mouseout', (e) => {
            if (e.target.closest('.rating-section .rating-input')) {
                this.clearRatingHover(e.target.closest('.rating-section .rating-input'));
            }
        });
        
        console.log('事件监听器绑定完成');
    }

    async handleLike(button) {
        const contentId = button.dataset.id;
        const contentType = button.dataset.type;
        
        if (!contentId || !contentType) {
            this.showMessage('参数错误', 'error');
            return;
        }

        try {
            button.disabled = true;
            console.log('发送点赞请求:', { id: parseInt(contentId), type: contentType });
            
            const response = await fetch('/api/like', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    id: parseInt(contentId),
                    type: contentType
                })
            });

            console.log('点赞响应状态:', response.status);
            
            if (response.status === 401) {
                this.showMessage('请先登录', 'error');
                return;
            }
            
            const result = await response.json();
            console.log('点赞响应结果:', result);
            
            if (result.success) {
                this.updateLikeUI(button, result.is_liked, result.like_count);
                this.updateFloatingLikeUI(contentId, contentType, result.is_liked, result.like_count);
                this.showMessage(result.is_liked ? '点赞成功' : '取消点赞', result.is_liked ? 'success' : 'info');
            } else {
                this.showMessage(result.message || '操作失败', 'error');
            }
        } catch (error) {
            console.error('点赞操作失败:', error);
            this.showMessage('网络错误，请重试', 'error');
        } finally {
            button.disabled = false;
        }
    }

    async handleFavorite(button) {
        const contentId = button.dataset.id;
        const contentType = button.dataset.type;
        
        if (!contentId || !contentType) {
            this.showMessage('参数错误', 'error');
            return;
        }

        try {
            button.disabled = true;
            console.log('发送收藏请求:', { id: parseInt(contentId), type: contentType });
            
            const response = await fetch('/api/favorite', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    id: parseInt(contentId),
                    type: contentType
                })
            });

            console.log('收藏响应状态:', response.status);
            
            if (response.status === 401) {
                this.showMessage('请先登录', 'error');
                return;
            }
            
            const result = await response.json();
            console.log('收藏响应结果:', result);
            
            if (result.success) {
                this.updateFavoriteUI(button, result.is_favorited, result.favorite_count);
                this.updateFloatingFavoriteUI(contentId, contentType, result.is_favorited, result.favorite_count);
                this.showMessage(result.is_favorited ? '收藏成功' : '取消收藏', result.is_favorited ? 'success' : 'info');
            } else {
                this.showMessage(result.message || '操作失败', 'error');
            }
        } catch (error) {
            console.error('收藏操作失败:', error);
            this.showMessage('网络错误，请重试', 'error');
        } finally {
            button.disabled = false;
        }
    }

    async handleCommentLike(button) {
        const commentId = button.dataset.commentId;
        
        if (!commentId) {
            this.showMessage('参数错误', 'error');
            return;
        }

        if (!this.currentUser) {
            this.showMessage('请先登录', 'error');
            return;
        }

        try {
            button.disabled = true;
            console.log('发送评论点赞请求:', { commentId: parseInt(commentId) });
            
            const response = await fetch('/api/comment-like', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    comment_id: parseInt(commentId)
                })
            });

            console.log('评论点赞响应状态:', response.status);
            
            if (response.status === 401) {
                this.showMessage('请先登录', 'error');
                return;
            }

            const result = await response.json();
            console.log('评论点赞响应结果:', result);

            if (result.success) {
                // 更新按钮状态
                const icon = button.querySelector('i');
                const countSpan = button.querySelector('.like-count');
                
                if (result.liked) {
                    // 已点赞
                    icon.className = 'fas fa-heart';
                    button.classList.add('liked');
                } else {
                    // 取消点赞
                    icon.className = 'far fa-heart';
                    button.classList.remove('liked');
                }
                
                // 更新点赞数
                if (countSpan) {
                    countSpan.textContent = result.like_count;
                }
                
                this.showMessage(result.message, 'success');
            } else {
                this.showMessage(result.message || '操作失败', 'error');
            }
        } catch (error) {
            console.error('评论点赞操作失败:', error);
            this.showMessage('操作失败，请稍后重试', 'error');
        } finally {
            button.disabled = false;
        }
    }

    handleRatingChange(radio) {
        const ratingSection = radio.closest('.rating-section') || radio.closest('.floating-rating-section');
        let interactionButtons, likeBtn;
        
        if (ratingSection.closest('.interaction-buttons')) {
            // 普通互动按钮
            interactionButtons = ratingSection.closest('.interaction-buttons');
            likeBtn = interactionButtons.querySelector('.like-btn');
        } else if (ratingSection.closest('.floating-interaction-buttons')) {
            // 悬浮互动按钮
            likeBtn = ratingSection.closest('.floating-interaction-buttons').querySelector('.like-btn');
        }
        
        if (!likeBtn) return;
        
        const contentId = likeBtn.dataset.id;
        const contentType = likeBtn.dataset.type;
        const rating = parseInt(radio.value);

        console.log('评分选择:', { contentId, contentType, rating });
        
        // 立即保存评分
        this.saveRating(contentId, contentType, rating);
    }

    async saveRating(contentId, contentType, rating) {
        try {
            console.log('保存评分:', {
                id: parseInt(contentId),
                type: contentType,
                rating: rating
            });

            const response = await fetch('/api/rating', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    id: parseInt(contentId),
                    type: contentType,
                    rating: rating
                })
            });

            if (response.status === 401) {
                this.showMessage('请先登录', 'error');
                return;
            }
            
            const result = await response.json();
            
            if (result.success) {
                this.updateRating(contentId, contentType, result.average_rating);
                console.log('评分保存成功');
            } else {
                console.error('评分保存失败:', result.message);
            }
        } catch (error) {
            console.error('评分保存失败:', error);
        }
    }

    async handleComment(form) {
        const contentId = form.dataset.id;
        const contentType = form.dataset.type;
        
        if (!contentId || !contentType) {
            this.showMessage('参数错误', 'error');
            return;
        }

        // 尝试从简化版评论编辑器获取内容
        let content = '';
        const editorContainer = document.getElementById(`comment-editor-${contentId}`);
        
        if (editorContainer && window.SimpleCommentEditor) {
            // 查找简化版评论编辑器实例
            const editorInstance = editorContainer.simpleCommentEditor;
            
            if (editorInstance) {
                content = editorInstance.getContent().trim();
            }
        }
        
        // 如果富文本编辑器没有内容，尝试从隐藏的textarea获取
        if (!content) {
            const contentInput = form.querySelector('.comment-content');
            
            if (contentInput) {
                content = contentInput.value.trim();
            }
        }

        // 提交时校验评论内容
        if (!content) {
            this.showMessage('请输入评论内容', 'error');
            return;
        }

        // 处理Base64图片
        content = await this.processBase64Images(content);

        // 对于富文本内容，检查纯文本长度
        const textContent = this.stripHtml(content);
        if (textContent.length > 1000) {
            this.showMessage('评论内容过长', 'error');
            return;
        }

        try {
            const submitBtn = form.querySelector('.comment-submit');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 提交中...';

            console.log('提交评论数据:', {
                id: parseInt(contentId),
                type: contentType,
                content: content
            });

            const response = await fetch('/api/comment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    id: parseInt(contentId),
                    type: contentType,
                    content: content
                })
            });

            console.log('评论响应状态:', response.status);
            
            if (response.status === 401) {
                this.showMessage('请先登录', 'error');
                return;
            }
            
            const result = await response.json();
            console.log('评论响应结果:', result);
            
            if (result.success) {
                this.showMessage('评论添加成功', 'success');
                
                // 清空富文本编辑器
                const editorContainer = document.getElementById(`comment-editor-${contentId}`);
                if (editorContainer && editorContainer.richTextEditor) {
                    editorContainer.richTextEditor.setContent('');
                }
                
                // 清空隐藏的textarea
                const contentInput = form.querySelector('.comment-content');
                if (contentInput) {
                    contentInput.value = '';
                }
                
                this.updateCommentCount(contentId, contentType, result.comment_count);
                this.loadCommentsForContent(contentId, contentType);
                
                // 如果有暂存的评分，一起提交
                if (this.tempRating && this.tempRating.contentId === contentId && this.tempRating.contentType === contentType) {
                    await this.saveRating(this.tempRating.contentId, this.tempRating.contentType, this.tempRating.rating);
                    this.tempRating = null; // 清空暂存的评分
                }
            } else {
                this.showMessage(result.message || '评论失败', 'error');
            }
        } catch (error) {
            console.error('评论操作失败:', error);
            this.showMessage('网络错误，请重试', 'error');
        } finally {
            const submitBtn = form.querySelector('.comment-submit');
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> 提交评论';
        }
    }

    updateLikeUI(button, isLiked, count) {
        const icon = button.querySelector('i');
        const countSpan = button.querySelector('.count');
        
        if (isLiked) {
            icon.className = 'fas fa-heart';
            button.classList.add('liked');
        } else {
            icon.className = 'far fa-heart';
            button.classList.remove('liked');
        }
        
        if (countSpan) {
            countSpan.textContent = count;
        }
    }

    updateFavoriteUI(button, isFavorited, count) {
        const icon = button.querySelector('i');
        const countSpan = button.querySelector('.count');
        
        if (isFavorited) {
            icon.className = 'fas fa-star';
            button.classList.add('favorited');
        } else {
            icon.className = 'far fa-star';
            button.classList.remove('favorited');
        }
        
        if (countSpan) {
            countSpan.textContent = count;
        }
    }
    
    // 更新悬浮点赞按钮UI
    updateFloatingLikeUI(contentId, contentType, isLiked, count) {
        const floatingButtons = document.querySelector('.floating-interaction-buttons');
        if (!floatingButtons) return;
        
        const likeBtn = floatingButtons.querySelector('.like-btn');
        if (likeBtn && likeBtn.dataset.id === contentId && likeBtn.dataset.type === contentType) {
            this.updateLikeUI(likeBtn, isLiked, count);
        }
    }
    
    // 更新悬浮收藏按钮UI
    updateFloatingFavoriteUI(contentId, contentType, isFavorited, count) {
        const floatingButtons = document.querySelector('.floating-interaction-buttons');
        if (!floatingButtons) return;
        
        const favoriteBtn = floatingButtons.querySelector('.favorite-btn');
        if (favoriteBtn && favoriteBtn.dataset.id === contentId && favoriteBtn.dataset.type === contentType) {
            this.updateFavoriteUI(favoriteBtn, isFavorited, count);
        }
    }

    updateRatingUI(element, userRating) {
        const ratingSection = element.querySelector('.rating-section') || element.querySelector('.floating-rating-section');
        if (!ratingSection) return;
        
        const ratingInputs = ratingSection.querySelectorAll('input[name="rating"]');
        
        // 清除所有选中状态
        ratingInputs.forEach(input => {
            input.checked = false;
        });
        
        // 设置用户评分
        if (userRating && userRating > 0) {
            const targetInput = ratingSection.querySelector(`input[name="rating"][value="${userRating}"]`);
            if (targetInput) {
                targetInput.checked = true;
            }
        }
    }

    updateCommentCount(contentId, contentType, count) {
        const commentCountElement = document.querySelector(`[data-id="${contentId}"][data-type="${contentType}"] .comment-count`);
        if (commentCountElement) {
            commentCountElement.textContent = count;
        }
    }

    updateRating(contentId, contentType, rating) {
        const ratingElement = document.querySelector(`[data-id="${contentId}"][data-type="${contentType}"] .rating-display`);
        if (ratingElement && rating > 0) {
            ratingElement.innerHTML = this.generateStarRating(rating);
        }
    }

    async loadUserStatus() {
        // 获取所有需要检查状态的内容
        const contentElements = document.querySelectorAll('[data-id][data-type]');
        
        for (const element of contentElements) {
            const contentId = element.dataset.id;
            const contentType = element.dataset.type;
            
            try {
                const response = await fetch(`/api/user-status/${contentId}?type=${contentType}`);
                const result = await response.json();
                
                if (result.success) {
                    const likeBtn = element.querySelector('.like-btn');
                    const favoriteBtn = element.querySelector('.favorite-btn');
                    
                    if (likeBtn) {
                        this.updateLikeUI(likeBtn, result.is_liked, likeBtn.querySelector('.count')?.textContent || 0);
                    }
                    
                    if (favoriteBtn) {
                        this.updateFavoriteUI(favoriteBtn, result.is_favorited, favoriteBtn.querySelector('.count')?.textContent || 0);
                    }
                    
                    // 更新评分状态
                    this.updateRatingUI(element, result.user_rating);
                    
                    // 更新悬浮按钮状态
                    this.updateFloatingButtonsStatus(contentId, contentType, result);
                }
            } catch (error) {
                console.error('获取用户状态失败:', error);
            }
        }
    }
    
    // 更新悬浮按钮状态
    updateFloatingButtonsStatus(contentId, contentType, result) {
        const floatingButtons = document.querySelector('.floating-interaction-buttons');
        if (!floatingButtons) return;
        
        const likeBtn = floatingButtons.querySelector('.like-btn');
        const favoriteBtn = floatingButtons.querySelector('.favorite-btn');
        const ratingSection = floatingButtons.querySelector('.floating-rating-section');
        
        // 检查是否是同一个内容
        if (likeBtn && likeBtn.dataset.id === contentId && likeBtn.dataset.type === contentType) {
            if (likeBtn) {
                this.updateLikeUI(likeBtn, result.is_liked, result.like_count || 0);
            }
            
            if (favoriteBtn) {
                this.updateFavoriteUI(favoriteBtn, result.is_favorited, result.favorite_count || 0);
            }
            
            if (ratingSection) {
                this.updateRatingUI(floatingButtons, result.user_rating);
            }
        }
    }

    async loadComments() {
        // 获取所有需要加载评论的内容
        const contentElements = document.querySelectorAll('[data-id][data-type]');
        
        for (const element of contentElements) {
            const contentId = element.dataset.id;
            const contentType = element.dataset.type;
            
            try {
                await this.loadCommentsForContent(contentId, contentType);
            } catch (error) {
                console.error('加载评论失败:', error);
            }
        }
    }

    async loadCommentsForContent(contentId, contentType, page = 1) {
        try {
            console.log('加载评论:', { contentId, contentType, page });
            const response = await fetch(`/api/comments/${contentId}?type=${contentType}&page=${page}`);
            const result = await response.json();
            
            console.log('评论加载结果:', result);
            
            if (result.success) {
                // 找到对应的评论容器
                const commentsContainer = document.querySelector(`.comments-list[data-content-id="${contentId}"][data-content-type="${contentType}"]`);
                if (commentsContainer) {
                    this.renderComments(result.comments, result.pagination, commentsContainer);
                } else {
                    console.error('未找到评论容器', { contentId, contentType });
                }
            }
        } catch (error) {
            console.error('加载评论失败:', error);
        }
    }


    renderComments(comments, pagination, commentsContainer = null) {
        if (!commentsContainer) {
            commentsContainer = document.querySelector('.comments-list');
        }
        if (!commentsContainer) return;

        let html = '';
        
        if (comments.length === 0) {
            html = '<div class="no-comments">暂无评论，快来抢沙发吧！</div>';
        } else {
            comments.forEach((comment, index) => {
                // 使用随机头像作为默认头像
                const defaultAvatar = this.generateRandomAvatar(comment.user.username);
                const avatar = comment.user.avatar || defaultAvatar;
                const avatarId = `comment-avatar-${comment.id}`;
                html += `
                    <div class="comment-item" data-comment-id="${comment.id}">
                        <div class="comment-header">
                            <img src="${avatar}" alt="${comment.user.username}" class="comment-avatar" id="${avatarId}" data-original-src="${avatar}" data-retry-count="0">
                            <div class="comment-info">
                                <span class="comment-author">${comment.user.username}</span>
                                <span class="comment-time">${comment.created_at}</span>
                            </div>
                            ${this.shouldShowCommentActions(comment.user.id) ? `
                            <div class="comment-actions" data-user-id="${comment.user.id}">
                                <button class="btn-delete-comment" data-comment-id="${comment.id}" title="删除评论">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                            ` : ''}
                        </div>
                        <div class="comment-content">${comment.content}</div>
                        <div class="comment-replies">
                            <div class="replies-list" data-comment-id="${comment.id}">
                                ${this.renderReplies(comment.replies || [])}
                            </div>
                            <div class="reply-form" style="display: none;" data-comment-id="${comment.id}">
                                <div class="reply-simple-editor-container"></div>
                                <div class="reply-actions">
                                    <button class="btn-submit-reply" data-comment-id="${comment.id}">
                                        <i class="fas fa-paper-plane"></i>
                                        回复
                                    </button>
                                    <button class="btn-cancel-reply" data-comment-id="${comment.id}">
                                        <i class="fas fa-times"></i>
                                        取消
                                    </button>
                                </div>
                            </div>
                            <div class="comment-footer">
                                <button class="btn-reply" data-comment-id="${comment.id}">
                                    <i class="fas fa-reply"></i> 回复
                                    ${comment.replies_count > 0 ? `(${comment.replies_count})` : ''}
                                </button>
                                <div class="comment-actions">
                                    <button class="comment-like-btn ${comment.is_liked ? 'liked' : ''}" 
                                            data-comment-id="${comment.id}" 
                                            title="${comment.is_liked ? '取消点赞' : '点赞'}">
                                        <i class="${comment.is_liked ? 'fas' : 'far'} fa-heart"></i>
                                        <span class="like-count">${comment.like_count || 0}</span>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
        }

        commentsContainer.innerHTML = html;
        
        // 为所有头像添加智能加载处理
        this.setupAvatarLoading(commentsContainer);
        
        // 为所有评论添加操作按钮事件
        this.setupCommentActions(commentsContainer);
        
        // 为所有回复按钮添加事件
        this.setupReplyActions(commentsContainer);
    }

    setupAvatarLoading(container) {
        const avatarImages = container.querySelectorAll('.comment-avatar');
        avatarImages.forEach(img => {
            img.addEventListener('error', (e) => {
                this.handleAvatarError(e.target);
            });
        });
    }

    setupCommentActions(container) {
        // 删除按钮事件
        container.querySelectorAll('.btn-delete-comment').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const deleteBtn = e.target.closest('.btn-delete-comment');
                if (deleteBtn && deleteBtn.dataset.commentId) {
                    const commentId = deleteBtn.dataset.commentId;
                    this.deleteComment(commentId);
                } else {
                    console.error('无法找到评论ID');
                }
            });
        });

    }

    handleAvatarError(img) {
        const retryCount = parseInt(img.dataset.retryCount) || 0;
        const maxRetries = 3;
        
        if (retryCount < maxRetries) {
            // 增加重试次数
            img.dataset.retryCount = retryCount + 1;
            
            // 添加重试延迟，避免频繁请求
            setTimeout(() => {
                // 重新尝试加载原始头像
                const originalSrc = img.dataset.originalSrc;
                if (originalSrc && !originalSrc.includes('/static/images/default-avatar.png')) {
                    img.src = originalSrc;
                } else {
                    // 如果原始头像就是默认头像，使用随机头像
                    const username = img.alt;
                    const defaultAvatar = this.generateRandomAvatar(username);
                    img.src = defaultAvatar;
                }
            }, 1000 * (retryCount + 1)); // 递增延迟：1秒、2秒、3秒
        } else {
            // 达到最大重试次数，使用随机头像
            const username = img.alt;
            const defaultAvatar = this.generateRandomAvatar(username);
            img.src = defaultAvatar;
            img.dataset.retryCount = maxRetries; // 标记为已完成重试
        }
    }

    generateStarRating(rating) {
        let html = '';
        
        for (let i = 1; i <= 5; i++) {
            if (i <= rating) {
                html += '<i class="fas fa-star"></i>';
            } else {
                html += '<i class="far fa-star"></i>';
            }
        }
        
        return html;
    }

    hashCode(str) {
        let hash = 0;
        if (str.length === 0) return hash;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32bit integer
        }
        return Math.abs(hash).toString(16);
    }

    generateRandomAvatar(username) {
        // 基于用户名生成一致的随机头像，使用4个头像
        const hash = this.hashCode(username);
        const avatarIndex = parseInt(hash.substring(0, 2), 16) % 4; // 0-3
        return `/static/avatar/avatar${avatarIndex + 1}.png`;
    }

    shouldShowCommentActions(commentUserId) {
        // 显示编辑/删除按钮的条件：
        // 1. 当前用户已登录
        // 2. 当前用户是评论作者 或 当前用户是管理员
        return this.currentUser && 
               (this.currentUser.id === commentUserId || this.isAdmin);
    }

    // 评论编辑功能已移除 - 评论不可修改

    async deleteComment(commentId) {
        if (!confirm('确定要删除这条评论吗？')) {
            return;
        }

        try {
            const response = await fetch(`/api/comment/${commentId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.status === 401) {
                this.showMessage('请先登录', 'error');
                return;
            }

            const result = await response.json();
            
            if (result.success) {
                this.showMessage('评论删除成功', 'success');
                
                // 获取评论元素和关联信息
                const commentItem = document.querySelector(`[data-comment-id="${commentId}"]`);
                if (commentItem) {
                    const interactionSection = commentItem.closest('[data-content-id]');
                    if (interactionSection) {
                        const contentId = interactionSection.dataset.contentId;
                        const contentType = interactionSection.dataset.contentType;
                        
                        // 更新评论计数和平均评分
                        this.updateCommentCount(contentId, contentType, result.comment_count);
                        this.updateRating(contentId, contentType, result.average_rating);
                    }
                    
                    // 移除评论元素
                    commentItem.remove();
                }
            } else {
                this.showMessage(result.message || '评论删除失败', 'error');
            }
        } catch (error) {
            console.error('评论删除失败:', error);
            this.showMessage('网络错误，请重试', 'error');
        }
    }

    handleRatingHover(target) {
        const label = target.closest('label');
        if (!label) return;

        const ratingContainer = label.closest('.rating-section .rating-input');
        if (!ratingContainer) return;

        // 清除所有悬停效果
        this.clearRatingHover(ratingContainer);

        // 获取当前星星的索引
        const labels = ratingContainer.querySelectorAll('label');
        const currentIndex = Array.from(labels).indexOf(label);
        
        // 为当前星星及之前的星星添加悬停效果
        for (let i = 0; i <= currentIndex; i++) {
            labels[i].classList.add('hover-active');
        }
    }

    clearRatingHover(ratingContainer) {
        if (!ratingContainer) return;
        
        const labels = ratingContainer.querySelectorAll('label');
        labels.forEach(label => {
            label.classList.remove('hover-active');
        });
    }

    stripHtml(html) {
        // 移除HTML标签，获取纯文本内容
        const temp = document.createElement('div');
        temp.innerHTML = html;
        return temp.textContent || temp.innerText || '';
    }

    async processBase64Images(content) {
        // 查找所有Base64图片
        const base64Regex = /<img[^>]+src="data:image\/[^;]+;base64,[^"]+"/g;
        const matches = content.match(base64Regex);
        
        if (!matches) {
            return content;
        }

        this.showMessage('正在处理图片...', 'info');

        let processedContent = content;
        
        for (const match of matches) {
            try {
                // 提取Base64数据
                const srcMatch = match.match(/src="data:image\/([^;]+);base64,([^"]+)"/);
                if (srcMatch) {
                    const mimeType = srcMatch[1];
                    const base64Data = srcMatch[2];
                    
                    // 将Base64转换为Blob
                    const byteCharacters = atob(base64Data);
                    const byteNumbers = new Array(byteCharacters.length);
                    for (let i = 0; i < byteCharacters.length; i++) {
                        byteNumbers[i] = byteCharacters.charCodeAt(i);
                    }
                    const byteArray = new Uint8Array(byteNumbers);
                    const blob = new Blob([byteArray], { type: `image/${mimeType}` });
                    
                    // 创建File对象
                    const file = new File([blob], `image.${mimeType}`, { type: `image/${mimeType}` });
                    
                    // 压缩并上传图片
                    const compressedFile = await this.compressImage(file);
                    const imageUrl = await this.uploadImageToServer(compressedFile);
                    
                    if (imageUrl) {
                        // 替换Base64图片为服务器URL
                        processedContent = processedContent.replace(match, match.replace(/src="data:image\/[^;]+;base64,[^"]+"/, `src="${imageUrl}"`));
                    }
                }
            } catch (error) {
                console.error('处理Base64图片失败:', error);
                // 如果处理失败，移除这个图片
                processedContent = processedContent.replace(match, '');
            }
        }

        return processedContent;
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
                    
                    resolve(compressedFile);
                }, 'image/jpeg', compressionQuality);
            };
            
            img.onerror = () => {
                // 如果图片加载失败，返回原文件
                resolve(file);
            };
            
            // 加载图片
            const reader = new FileReader();
            reader.onload = (e) => {
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        });
    }

    async uploadImageToServer(file) {
        try {
            // 创建FormData对象
            const formData = new FormData();
            formData.append('image', file);
            
            // 发送到服务器上传
            const response = await fetch('/api/upload-image', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const result = await response.json();
                if (result.success) {
                    return result.image_url;
                } else {
                    console.error('图片上传失败:', result.message);
                    return null;
                }
            } else {
                throw new Error('上传失败');
            }
        } catch (error) {
            console.error('图片上传错误:', error);
            return null;
        }
    }

    showMessage(message, type = 'info', duration = 3000) {
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

    // 回复相关函数
    renderReplies(replies) {
        if (!replies || replies.length === 0) {
            return '';
        }
        
        return replies.map(reply => {
            const defaultAvatar = this.generateRandomAvatar(reply.user.username);
            const avatar = reply.user.avatar || defaultAvatar;
            return `
                <div class="reply-item" data-reply-id="${reply.id}">
                    <div class="reply-header">
                        <img src="${avatar}" alt="${reply.user.username}" class="reply-avatar">
                        <div class="reply-info">
                            <span class="reply-author">${reply.user.username}</span>
                            <span class="reply-time">${reply.created_at}</span>
                        </div>
                        ${this.shouldShowReplyActions(reply.user.id) ? `
                        <div class="reply-actions">
                            <button class="btn-delete-reply" data-reply-id="${reply.id}" title="删除回复">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                        ` : ''}
                    </div>
                    <div class="reply-content">${reply.content}</div>
                </div>
            `;
        }).join('');
    }

    setupReplyActions(container) {
        // 回复按钮事件
        container.querySelectorAll('.btn-reply').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const replyBtn = e.target.closest('.btn-reply');
                if (replyBtn && replyBtn.dataset.commentId) {
                    const commentId = replyBtn.dataset.commentId;
                    this.showReplyForm(commentId);
                } else {
                    console.error('无法找到评论ID');
                }
            });
        });

        // 提交回复按钮事件
        container.querySelectorAll('.btn-submit-reply').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const submitBtn = e.target.closest('.btn-submit-reply');
                if (submitBtn && submitBtn.dataset.commentId) {
                    const commentId = submitBtn.dataset.commentId;
                    this.submitReply(commentId);
                } else {
                    console.error('无法找到评论ID');
                }
            });
        });

        // 取消回复按钮事件
        container.querySelectorAll('.btn-cancel-reply').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const cancelBtn = e.target.closest('.btn-cancel-reply');
                if (cancelBtn && cancelBtn.dataset.commentId) {
                    const commentId = cancelBtn.dataset.commentId;
                    this.hideReplyForm(commentId);
                } else {
                    console.error('无法找到评论ID');
                }
            });
        });

        // 回复编辑功能已移除

        // 删除回复按钮事件
        container.querySelectorAll('.btn-delete-reply').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const deleteBtn = e.target.closest('.btn-delete-reply');
                if (deleteBtn && deleteBtn.dataset.replyId) {
                    const replyId = deleteBtn.dataset.replyId;
                    this.deleteReply(replyId);
                } else {
                    console.error('无法找到回复ID');
                }
            });
        });

        // 回复编辑功能已移除
    }

    showReplyForm(commentId) {
        const replyForm = document.querySelector(`.reply-form[data-comment-id="${commentId}"]`);
        if (replyForm) {
            replyForm.style.display = 'block';
            
            // 初始化简化版评论编辑器
            const editorContainer = replyForm.querySelector('.reply-simple-editor-container');
            if (editorContainer) {
                // 检查是否已经初始化
                if (!editorContainer.simpleCommentEditor && (!editorContainer.dataset || editorContainer.dataset.initialized !== 'true')) {
                    try {
                        const editor = new SimpleCommentEditor(editorContainer, {
                            placeholder: '回复评论...',
                            content: ''
                        });
                        editorContainer.simpleCommentEditor = editor;
                        editorContainer.dataset.initialized = 'true';
                        editorContainer.dataset.editorInstance = 'reply-editor';
                        editor.focus();
                        console.log('回复简化版评论编辑器初始化成功');
                    } catch (error) {
                        console.error('回复简化版评论编辑器初始化失败:', error);
                    }
                } else if (editorContainer.simpleCommentEditor) {
                    // 如果已经初始化，清空内容并聚焦
                    editorContainer.simpleCommentEditor.clear();
                    editorContainer.simpleCommentEditor.focus();
                }
            }
        }
    }

    hideReplyForm(commentId) {
        const replyForm = document.querySelector(`.reply-form[data-comment-id="${commentId}"]`);
        if (replyForm) {
            replyForm.style.display = 'none';
            
            // 清空简化版评论编辑器内容
            const editorContainer = replyForm.querySelector('.reply-simple-editor-container');
            if (editorContainer) {
                if (editorContainer.simpleCommentEditor) {
                    // 使用简化版评论编辑器实例清空内容
                    editorContainer.simpleCommentEditor.clear();
                }
            }
        }
    }

    async submitReply(commentId) {
        const replyForm = document.querySelector(`.reply-form[data-comment-id="${commentId}"]`);
        if (!replyForm) {
            console.error('回复表单未找到:', commentId);
            return;
        }

        // 从简化版评论编辑器获取内容
        const editorContainer = replyForm.querySelector('.reply-simple-editor-container');
        let content = '';
        
        if (editorContainer) {
            // 检查简化版评论编辑器是否已初始化
            if (editorContainer.simpleCommentEditor) {
                // 使用简化版评论编辑器实例获取内容
                content = editorContainer.simpleCommentEditor.getContent().trim();
            } else {
                console.warn('简化版评论编辑器未正确初始化');
            }
        }
        
        // 检查纯文本内容
        const textContent = this.stripHtml(content);
        if (!textContent) {
            this.showMessage('请输入回复内容', 'error');
            return;
        }
        
        // 处理Base64图片
        content = await this.processBase64Images(content);

        const submitBtn = replyForm.querySelector('.btn-submit-reply');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 回复中...';

        try {
            const response = await fetch(`/api/comments/${commentId}/replies`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ content })
            });

            if (response.status === 401) {
                this.showMessage('请先登录', 'error');
                return;
            }

            const result = await response.json();

            if (result.success) {
                this.showMessage('回复成功', 'success');
                
                // 清空简化版评论编辑器内容
                if (editorContainer && editorContainer.simpleCommentEditor) {
                    editorContainer.simpleCommentEditor.clear();
                }
                
                this.hideReplyForm(commentId);
                // 重新加载评论以显示新回复
                const commentItem = document.querySelector(`[data-comment-id="${commentId}"]`);
                if (commentItem) {
                    const contentElement = commentItem.closest('[data-id]');
                    const typeElement = commentItem.closest('[data-type]');
                    
                    if (contentElement && typeElement) {
                        const contentId = contentElement.dataset.id;
                        const contentType = typeElement.dataset.type;
                        this.loadCommentsForContent(contentId, contentType);
                    } else {
                        console.warn('无法找到内容ID或类型元素，跳过重新加载评论');
                    }
                }
            } else {
                this.showMessage(result.message || '回复失败', 'error');
            }
        } catch (error) {
            console.error('回复操作失败:', error);
            this.showMessage('网络错误，请重试', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '回复';
        }
    }

    shouldShowReplyActions(userId) {
        return this.currentUser && (this.currentUser.id === userId || this.isAdmin);
    }

    // 回复编辑功能已移除 - 回复不可修改

    async deleteReply(replyId) {
        if (!confirm('确定要删除这条回复吗？')) {
            return;
        }

        try {
            const response = await fetch(`/api/replies/${replyId}`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (result.success) {
                this.showMessage('回复删除成功', 'success');
                // 移除回复元素
                const replyItem = document.querySelector(`.reply-item[data-reply-id="${replyId}"]`);
                if (replyItem) {
                    replyItem.remove();
                }
            } else {
                this.showMessage(result.message || '删除失败', 'error');
            }
        } catch (error) {
            console.error('删除回复失败:', error);
            this.showMessage('网络错误，请重试', 'error');
        }
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('InteractionManager 正在初始化...');
    try {
        new InteractionManager();
        console.log('InteractionManager 初始化成功');
    } catch (error) {
        console.error('InteractionManager 初始化失败:', error);
    }
});
