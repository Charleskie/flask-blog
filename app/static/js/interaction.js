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
                this.isGuest = result.is_guest || false;
                
                // 如果是访客模式，更新UI状态
                if (this.isGuest) {
                    this.updateGuestModeUI();
                }
            } else if (response.status === 401) {
                this.isGuest = true;
                this.updateGuestModeUI();
            }
        } catch (error) {
            // 静默处理错误
        }
    }

    updateGuestModeUI() {
        const likeButtons = document.querySelectorAll('.like-btn');
        likeButtons.forEach(btn => {
            btn.title = '登录后可点赞';
        });
        
        const favoriteButtons = document.querySelectorAll('.favorite-btn');
        favoriteButtons.forEach(btn => {
            btn.title = '登录后可收藏';
        });
    }

    showLoginModal(message) {
        const modal = document.getElementById('loginModal');
        if (modal) {
            const msgEl = document.getElementById('loginModalMessage');
            if (msgEl && message) {
                msgEl.textContent = message;
            }
            modal.classList.remove('d-none');
            modal.classList.add('d-flex');
            document.body.classList.add('has-site-dialog');
            modal.onclick = function(e) {
                if (e.target === modal) {
                    modal.classList.add('d-none');
                    modal.classList.remove('d-flex');
                    document.body.classList.remove('has-site-dialog');
                }
            };
        } else {
            this.showMessage(message || '请先登录后再操作', 'warning');
        }
    }

    bindEvents() {
        // 点赞按钮事件
        document.addEventListener('click', (e) => {
            
            if (e.target.closest('.like-btn')) {
                e.preventDefault();
                this.handleLike(e.target.closest('.like-btn'));
            }
            
            if (e.target.closest('.favorite-btn')) {e.preventDefault();
                this.handleFavorite(e.target.closest('.favorite-btn'));
            }
            
            if (e.target.closest('.comment-like-btn')) {e.preventDefault();
                this.handleCommentLike(e.target.closest('.comment-like-btn'));
            }
            
             // 评论提交按钮事件
            if (e.target.closest('.comment-submit')) {e.preventDefault();
                const form = e.target.closest('.comment-form');
                if (form) {
                    this.handleComment(form);
                }
            }
        });

        // 评分选择事件 - 自动保存评分
        document.addEventListener('change', (e) => {
            if (e.target.name === 'rating' && (e.target.closest('.rating-section') || e.target.closest('.floating-rating-section'))) {this.handleRatingChange(e.target);
            }
        });

        // 评分悬停事件（仅限互动统计模块）
        document.addEventListener('mouseover', (e) => {
            if (e.target.closest('.rating-input label')) {
                this.handleRatingHover(e.target);
            }
        });

        document.addEventListener('mouseout', (e) => {
            const ratingContainer = e.target.closest('.rating-input');
            if (ratingContainer && !ratingContainer.contains(e.relatedTarget)) {
                this.clearRatingHover(ratingContainer);
            }
        });

    }

    updateRatingLabelIcon(label, filled) {
        const icon = label.querySelector('i');
        if (!icon) return;

        icon.className = 'fas fa-star';
    }

    syncRatingVisualState(ratingContainer) {
        if (!ratingContainer) return;

        const checkedInput = ratingContainer.querySelector('input[name="rating"]:checked');
        const activeRating = checkedInput ? parseInt(checkedInput.value, 10) : 0;
        const labels = ratingContainer.querySelectorAll('label');

        labels.forEach(label => {
            label.classList.remove('hover-active');

            const labelRating = parseInt(label.dataset.rating || '0', 10);
            const filled = activeRating > 0 && labelRating <= activeRating;

            label.classList.toggle('is-active', filled);
            this.updateRatingLabelIcon(label, filled);
        });
    }

    async handleLike(button) {
        if (this.isGuest || !this.currentUser) {
            this.showLoginModal('登录后即可为内容点赞');
            return;
        }
        
        const contentId = button.dataset.id;
        const contentType = button.dataset.type;
        
        if (!contentId || !contentType) {
            this.showMessage('参数错误', 'error');
            return;
        }

        try {
            button.disabled = true;
            
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
            
            if (response.status === 401) {
                this.showMessage('请先登录', 'error');
                return;
            }
            
            const result = await response.json();
            
            if (result.success) {
                this.updateLikeUI(button, result.is_liked, result.like_count);
                this.updateFloatingLikeUI(contentId, contentType, result.is_liked, result.like_count);
                this.showMessage(result.is_liked ? '点赞成功' : '取消点赞', result.is_liked ? 'success' : 'info');
            } else {
                if (result.require_login) {
                    this.showMessage('请先登录后再进行点赞操作', 'warning');
                } else {
                    this.showMessage(result.message || '操作失败', 'error');
                }
            }
        } catch (error) {
            console.error('点赞操作失败:', error);
            this.showMessage('网络错误，请重试', 'error');
        } finally {
            button.disabled = false;
        }
    }

    async handleFavorite(button) {
        if (this.isGuest || !this.currentUser) {
            this.showLoginModal('登录后即可收藏喜欢的内容');
            return;
        }
        
        const contentId = button.dataset.id;
        const contentType = button.dataset.type;
        
        if (!contentId || !contentType) {
            this.showMessage('参数错误', 'error');
            return;
        }

        try {
            button.disabled = true;
            
            const response = await fetch('/api/favorite', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    id: parseInt(contentId),
                    type: contentType
                })
            });if (response.status === 401) {
                this.showMessage('请先登录', 'error');
                return;
            }
            
            const result = await response.json();if (result.success) {
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
        if (this.isGuest || !this.currentUser) {
            this.showLoginModal('登录后即可为评论点赞');
            return;
        }
        
        const commentId = button.dataset.commentId;
        
        if (!commentId) {
            this.showMessage('参数错误', 'error');
            return;
        }

        try {
            button.disabled = true;
            
            const response = await fetch('/api/comment-like', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    comment_id: parseInt(commentId)
                })
            });if (response.status === 401) {
                this.showMessage('请先登录', 'error');
                return;
            }

            const result = await response.json();if (result.success) {
                const icon = button.querySelector('i');
                const countSpan = button.querySelector('.action-text');
                
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
        const ratingContainer = ratingSection ? ratingSection.querySelector('.rating-input') : null;

        if (this.isGuest || !this.currentUser) {
            radio.checked = false;
            this.syncRatingVisualState(ratingContainer);
            this.showLoginModal('登录后即可为内容评分');
            return;
        }

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
        const rating = parseInt(radio.value, 10);

        this.syncRatingVisualState(ratingContainer);

        // 立即保存评分
        this.saveRating(contentId, contentType, rating);
    }

    async saveRating(contentId, contentType, rating) {
        try {

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
                this.updateRating(contentId, contentType, result.average_rating);} else {
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

            // 提交评论数据

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
            });if (response.status === 401) {
                this.showMessage('请先登录', 'error');
                return;
            }
            
            const result = await response.json();if (result.success) {
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

        this.syncRatingVisualState(ratingSection.querySelector('.rating-input'));
    }

    updateCommentCount(contentId, contentType, count) {
        const commentCountElement = document.querySelector(`[data-id="${contentId}"][data-type="${contentType}"] .comment-count`);
        if (commentCountElement) {
            commentCountElement.textContent = count;
        }
    }

    formatAverageRating(rating) {
        const numericRating = Number(rating);
        if (!Number.isFinite(numericRating) || numericRating <= 0) {
            return '暂无';
        }

        return numericRating.toFixed(1);
    }

    updateFloatingRatingSummary(contentId, contentType, rating) {
        const floatingButtons = document.querySelector('.floating-interaction-buttons');
        if (!floatingButtons) return;

        const likeBtn = floatingButtons.querySelector('.like-btn');
        if (!likeBtn || likeBtn.dataset.id !== contentId || likeBtn.dataset.type !== contentType) {
            return;
        }

        const ratingAverage = floatingButtons.querySelector('.floating-rating-average');
        if (ratingAverage) {
            ratingAverage.textContent = this.formatAverageRating(rating);
        }
    }

    updateRating(contentId, contentType, rating) {
        const ratingElement = document.querySelector(`[data-id="${contentId}"][data-type="${contentType}"] .rating-display`);
        if (ratingElement && rating > 0) {
            ratingElement.innerHTML = this.generateStarRating(rating);
        }

        this.updateFloatingRatingSummary(contentId, contentType, rating);
    }

    async loadUserStatus() {
        if (this.isGuest || !this.currentUser) return;
        
        const contentElements = document.querySelectorAll('[data-id][data-type]');
        
        for (const element of contentElements) {
            const contentId = element.dataset.id;
            const contentType = element.dataset.type;
            
            try {
                const response = await fetch(`/api/user-status/${contentId}?type=${contentType}`);
                const responseType = response.headers.get('content-type') || '';
                if (!responseType.includes('application/json')) {
                    continue;
                }

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
        try {const response = await fetch(`/api/comments/${contentId}?type=${contentType}&page=${page}`);
            const result = await response.json();if (result.success) {
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
        } else {
            comments.forEach((comment, index) => {
                // 使用随机头像作为默认头像
                const defaultAvatar = this.generateRandomAvatar(comment.user.username);
                const avatar = comment.user.avatar || defaultAvatar;
                const avatarId = `comment-avatar-${comment.id}`;
                html += `
                    <div class="comment-card" data-comment-id="${comment.id}">
                        <div class="comment-card-header">
                            <div class="comment-user-info">
                                <div class="comment-avatar-container">
                                    <img src="${avatar}" alt="${comment.user.username}" class="comment-avatar" id="${avatarId}" data-original-src="${avatar}" data-retry-count="0">
                                    <div class="avatar-status-indicator"></div>
                                </div>
                                <div class="comment-user-details">
                                    <div class="comment-author-name">${comment.user.username}</div>
                                    <div class="comment-meta">
                                        <span class="comment-time">
                                            <i class="fas fa-clock"></i>
                                            ${comment.created_at}
                                        </span>
                                        ${comment.replies_count > 0 ? `
                                        <span class="comment-replies-count">
                                            <i class="fas fa-reply"></i>
                                            ${comment.replies_count} 条回复
                                        </span>
                                        ` : ''}
                                    </div>
                                </div>
                            </div>
                            ${this.shouldShowCommentActions(comment.user.id) ? `
                            <div class="comment-admin-actions">
                                <button class="btn-admin-action btn-delete-comment" data-comment-id="${comment.id}" title="删除评论">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                            ` : ''}
                        </div>
                        
                        <div class="comment-card-body">
                            <div class="comment-content-wrapper">
                                <div class="comment-content">${comment.content}</div>
                            </div>
                        </div>
                        
                        <div class="comment-card-footer">
                            <div class="comment-actions-left">
                                <button class="btn-comment-action comment-like-btn ${comment.is_liked ? 'liked' : ''}" 
                                        data-comment-id="${comment.id}" 
                                        title="${comment.is_liked ? '取消点赞' : '点赞'}">
                                    <i class="${comment.is_liked ? 'fas' : 'far'} fa-heart"></i>
                                    <span class="action-text">${comment.like_count || 0}</span>
                                </button>
                                <button type="button" class="btn-comment-action btn-reply" data-comment-id="${comment.id}" aria-expanded="false">
                                    <i class="fas fa-reply"></i>
                                    <span class="action-text">回复</span>
                                </button>
                            </div>
                        </div>
                        
                        <div class="comment-replies-section">
                            <div class="replies-container" data-comment-id="${comment.id}">
                                <div class="replies-list" data-comment-id="${comment.id}">
                                    ${this.renderReplies(comment.id, comment.replies || [])}
                                </div>
                                <div
                                    class="reply-form"
                                    style="display: none;"
                                    data-comment-id="${comment.id}"
                                    data-base-reply-to-user-id="${comment.user.id}"
                                    data-base-reply-to-username="${comment.user.username}"
                                    data-parent-reply-id=""
                                    data-reply-to-user-id="${comment.user.id}"
                                    data-reply-to-username="${comment.user.username}"
                                >
                                    <div class="reply-form-header">
                                        <div class="reply-form-meta">
                                            <div class="reply-form-avatar">
                                                <img src="${this.currentUser?.avatar || this.generateRandomAvatar(this.currentUser?.username || 'user')}" alt="当前用户" class="reply-user-avatar">
                                            </div>
                                            <div class="reply-form-info">
                                                <div class="reply-form-user">
                                                    回复给
                                                    <span class="reply-form-target">@${comment.user.username}</span>
                                                </div>
                                                <div class="reply-form-hint">支持表情和图片</div>
                                            </div>
                                        </div>
                                        <button type="button" class="reply-form-close btn-admin-action" data-comment-id="${comment.id}" title="收起回复框">
                                            <i class="fas fa-times"></i>
                                        </button>
                                    </div>
                                    <div class="reply-editor-container">
                                        <div class="reply-simple-editor-container"></div>
                                    </div>
                                    <div class="reply-form-actions">
                                        <button type="button" class="btn-reply-action btn-submit-reply primary" data-comment-id="${comment.id}">
                                            <i class="fas fa-paper-plane"></i>
                                            发送回复
                                        </button>
                                    </div>
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
        const confirmed = await window.confirmAsync('确定要删除这条评论吗？', {
            title: '删除评论',
            confirmText: '确认删除',
            cancelText: '取消',
            danger: true
        });
        if (!confirmed) {
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
                        
                        this.updateCommentCount(contentId, contentType, result.comment_count);
                        if (result.average_rating !== undefined) {
                            this.updateRating(contentId, contentType, result.average_rating);
                        }
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

        const ratingContainer = label.closest('.rating-input');
        if (!ratingContainer) return;

        // 清除所有悬停效果
        this.clearRatingHover(ratingContainer);

        const previewRating = parseInt(label.dataset.rating || '0', 10);
        const labels = ratingContainer.querySelectorAll('label');
        
        labels.forEach(currentLabel => {
            const labelRating = parseInt(currentLabel.dataset.rating || '0', 10);
            const filled = previewRating > 0 && labelRating <= previewRating;

            currentLabel.classList.toggle('hover-active', filled);
            currentLabel.classList.toggle('is-active', false);
            this.updateRatingLabelIcon(currentLabel, filled);
        });
    }

    clearRatingHover(ratingContainer) {
        if (!ratingContainer) return;
        
        const labels = ratingContainer.querySelectorAll('label');
        labels.forEach(label => {
            label.classList.remove('hover-active');
        });

        this.syncRatingVisualState(ratingContainer);
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
                    return result.url || result.image_url;
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
        if (typeof window.showToast === 'function') {
            return window.showToast(message, type, duration);
        }
        return null;
    }

    // 回复相关函数
    renderReplies(commentId, replies) {
        if (!replies || replies.length === 0) {
            return '';
        }
        
        return replies.map(reply => {
            const defaultAvatar = this.generateRandomAvatar(reply.user.username);
            const avatar = reply.user.avatar || defaultAvatar;
            const replyContext = reply.parent_reply_id && reply.reply_to ? `
                <div class="reply-target-context">
                    回复 <span class="reply-target-name">@${reply.reply_to.username}</span>
                </div>
            ` : '';
            return `
                <div class="reply-card" data-reply-id="${reply.id}">
                    <div class="reply-card-header">
                        <div class="reply-user-info">
                            <div class="reply-avatar-container">
                                <img src="${avatar}" alt="${reply.user.username}" class="reply-avatar">
                                <div class="reply-avatar-indicator"></div>
                            </div>
                            <div class="reply-user-details">
                                <div class="reply-author-name">${reply.user.username}</div>
                                <div class="reply-meta">
                                    <span class="reply-time">
                                        <i class="fas fa-clock"></i>
                                        ${reply.created_at}
                                    </span>
                                </div>
                            </div>
                        </div>
                        ${this.shouldShowReplyActions(reply.user.id) ? `
                        <div class="reply-admin-actions">
                            <button class="btn-admin-action btn-delete-reply" data-reply-id="${reply.id}" title="删除回复">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                        ` : ''}
                    </div>
                    <div class="reply-card-body">
                        <div class="reply-content-wrapper">
                            ${replyContext}
                            <div class="reply-content">${reply.content}</div>
                        </div>
                    </div>
                    <div class="reply-card-footer">
                        <div class="reply-actions">
                            <button type="button" class="btn-reply-action reply-like-btn ${reply.is_liked ? 'liked' : ''}" 
                                    data-reply-id="${reply.id}" 
                                    title="${reply.is_liked ? '取消点赞' : '点赞'}">
                                <i class="${reply.is_liked ? 'fas' : 'far'} fa-heart"></i>
                                <span class="action-text">${reply.like_count || 0}</span>
                            </button>
                            <button
                                type="button"
                                class="btn-reply-action btn-reply-to-reply"
                                data-comment-id="${commentId}"
                                data-parent-reply-id="${reply.id}"
                                data-reply-to-user-id="${reply.user.id}"
                                data-reply-to-username="${reply.user.username}"
                            >
                                <i class="fas fa-reply"></i>
                                <span class="action-text">回复</span>
                            </button>
                        </div>
                    </div>
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
                    const replyForm = document.querySelector(`.reply-form[data-comment-id="${commentId}"]`);
                    if (replyForm && replyForm.classList.contains('is-open')) {
                        this.hideReplyForm(commentId);
                    } else {
                        this.showReplyForm(commentId);
                    }
                } else {
                    console.error('无法找到评论ID');
                }
            });
        });

        container.querySelectorAll('.btn-reply-to-reply').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const replyBtn = e.target.closest('.btn-reply-to-reply');
                if (replyBtn && replyBtn.dataset.commentId) {
                    this.showReplyForm(replyBtn.dataset.commentId, {
                        parentReplyId: replyBtn.dataset.parentReplyId,
                        replyToUserId: replyBtn.dataset.replyToUserId,
                        replyToUsername: replyBtn.dataset.replyToUsername
                    });
                } else {
                    console.error('无法找到回复目标');
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
        container.querySelectorAll('.reply-form-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const cancelBtn = e.target.closest('.reply-form-close');
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

    setReplyFormTarget(replyForm, options = {}) {
        const baseReplyToUserId = replyForm.dataset.baseReplyToUserId || '';
        const baseReplyToUsername = replyForm.dataset.baseReplyToUsername || '用户';
        const parentReplyId = options.parentReplyId ? String(options.parentReplyId) : '';
        const replyToUserId = options.replyToUserId ? String(options.replyToUserId) : baseReplyToUserId;
        const replyToUsername = options.replyToUsername || baseReplyToUsername;

        replyForm.dataset.parentReplyId = parentReplyId;
        replyForm.dataset.replyToUserId = replyToUserId;
        replyForm.dataset.replyToUsername = replyToUsername;

        const targetElement = replyForm.querySelector('.reply-form-target');
        if (targetElement) {
            targetElement.textContent = `@${replyToUsername}`;
        }

        const hintElement = replyForm.querySelector('.reply-form-hint');
        if (hintElement) {
            hintElement.textContent = parentReplyId ? '正在回复这条回复' : '支持表情和图片';
        }
    }

    setReplyButtonState(commentId, isActive) {
        document.querySelectorAll(`.btn-reply[data-comment-id="${commentId}"]`).forEach(btn => {
            btn.classList.toggle('active', isActive);
            btn.setAttribute('aria-expanded', isActive ? 'true' : 'false');
        });
    }

    hideAllReplyForms(exceptCommentId = null) {
        document.querySelectorAll('.reply-form').forEach(form => {
            const formCommentId = form.dataset.commentId;
            if (exceptCommentId !== null && String(formCommentId) === String(exceptCommentId)) {
                return;
            }

            form.style.display = 'none';
            form.classList.remove('is-open');
            this.setReplyFormTarget(form);
            this.setReplyButtonState(formCommentId, false);

            const editorContainer = form.querySelector('.reply-simple-editor-container');
            if (editorContainer && editorContainer.simpleCommentEditor) {
                editorContainer.simpleCommentEditor.clear();
            }
        });
    }

    showReplyForm(commentId, options = {}) {
        const replyForm = document.querySelector(`.reply-form[data-comment-id="${commentId}"]`);
        if (replyForm) {
            this.hideAllReplyForms(commentId);
            replyForm.style.display = 'block';
            replyForm.classList.add('is-open');
            this.setReplyFormTarget(replyForm, options);
            this.setReplyButtonState(commentId, true);

            const replyPlaceholder = replyForm.dataset.replyToUsername
                ? `回复 @${replyForm.dataset.replyToUsername}...`
                : '回复评论...';
            
            // 初始化简化版评论编辑器
            const editorContainer = replyForm.querySelector('.reply-simple-editor-container');
            if (editorContainer) {
                // 检查是否已经初始化
                if (!editorContainer.simpleCommentEditor && (!editorContainer.dataset || editorContainer.dataset.initialized !== 'true')) {
                    try {
                        const editor = new SimpleCommentEditor(editorContainer, {
                            placeholder: replyPlaceholder,
                            content: ''
                        });
                        editorContainer.simpleCommentEditor = editor;
                        editorContainer.dataset.initialized = 'true';
                        editorContainer.dataset.editorInstance = 'reply-editor';
                        editor.focus();} catch (error) {
                        console.error('回复简化版评论编辑器初始化失败:', error);
                    }
                } else if (editorContainer.simpleCommentEditor) {
                    // 如果已经初始化，清空内容并聚焦
                    const editorContent = editorContainer.querySelector('.comment-content');
                    if (editorContent) {
                        editorContent.dataset.placeholder = replyPlaceholder;
                    }
                    editorContainer.simpleCommentEditor.clear();
                    editorContainer.simpleCommentEditor.updatePlaceholder();
                    editorContainer.simpleCommentEditor.focus();
                }
            }
        }
    }

    hideReplyForm(commentId) {
        const replyForm = document.querySelector(`.reply-form[data-comment-id="${commentId}"]`);
        if (replyForm) {
            replyForm.style.display = 'none';
            replyForm.classList.remove('is-open');
            this.setReplyFormTarget(replyForm);
            this.setReplyButtonState(commentId, false);
            
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
            } else {}
        }
        
        // 检查纯文本内容
        const textContent = this.stripHtml(content);
        if (!textContent) {
            this.showMessage('请输入回复内容', 'error');
            return;
        }
        
        // 处理Base64图片
        content = await this.processBase64Images(content);

        const parentReplyId = replyForm.dataset.parentReplyId || '';

        const submitBtn = replyForm.querySelector('.btn-submit-reply');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 回复中...';

        try {
            const response = await fetch(`/api/comments/${commentId}/replies`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content,
                    parent_reply_id: parentReplyId || null
                })
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
                this.reloadCommentsForComment(commentId);
            } else {
                this.showMessage(result.message || '回复失败', 'error');
            }
        } catch (error) {
            console.error('回复操作失败:', error);
            this.showMessage('网络错误，请重试', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> 发送回复';
        }
    }

    shouldShowReplyActions(userId) {
        return this.currentUser && (this.currentUser.id === userId || this.isAdmin);
    }

    reloadCommentsForComment(commentId) {
        const commentItem = document.querySelector(`[data-comment-id="${commentId}"]`);
        if (!commentItem) {
            return;
        }

        const commentsList = commentItem.closest('.comments-list');
        if (!commentsList) {
            return;
        }

        const contentId = commentsList.dataset.contentId;
        const contentType = commentsList.dataset.contentType;

        if (contentId && contentType) {
            this.loadCommentsForContent(contentId, contentType);
        }
    }

    // 回复编辑功能已移除 - 回复不可修改

    async deleteReply(replyId) {
        const confirmed = await window.confirmAsync('确定要删除这条回复吗？', {
            title: '删除回复',
            confirmText: '确认删除',
            cancelText: '取消',
            danger: true
        });
        if (!confirmed) {
            return;
        }

        try {
            const response = await fetch(`/api/replies/${replyId}`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (result.success) {
                this.showMessage('回复删除成功', 'success');
                const replyItem = document.querySelector(`.reply-card[data-reply-id="${replyId}"]`);
                if (replyItem) {
                    const commentItem = replyItem.closest('[data-comment-id]');
                    const commentId = commentItem?.dataset.commentId;
                    if (commentId) {
                        this.reloadCommentsForComment(commentId);
                    } else {
                        replyItem.remove();
                    }
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
document.addEventListener('DOMContentLoaded', () => {try {
        new InteractionManager();} catch (error) {
        console.error('InteractionManager 初始化失败:', error);
    }
});
