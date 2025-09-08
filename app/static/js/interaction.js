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
            }
        } catch (error) {
            console.log('未登录或获取用户信息失败');
        }
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
            
//            if (e.target.closest('.comment-form')) {
//                console.log('评论表单被提交');
//                e.preventDefault();
//                this.handleComment(e.target.closest('.comment-form'));
//            }
        });

        // 评分选择事件 - 自动保存评分
        document.addEventListener('change', (e) => {
            if (e.target.name === 'rating') {
                console.log('评分被选择:', e.target.value);
                this.handleRatingChange(e.target);
            }
        });

        // 评分悬停事件
        document.addEventListener('mouseover', (e) => {
            if (e.target.closest('.rating-input label') || e.target.closest('.edit-rating-input .rating-stars label')) {
                this.handleRatingHover(e.target);
            }
        });

        document.addEventListener('mouseout', (e) => {
            if (e.target.closest('.rating-input') || e.target.closest('.edit-rating-input .rating-stars')) {
                this.clearRatingHover(e.target.closest('.rating-input') || e.target.closest('.edit-rating-input .rating-stars'));
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

    async handleRatingChange(radio) {
        const form = radio.closest('.comment-form');
        const contentId = form.dataset.id;
        const contentType = form.dataset.type;
        const rating = parseInt(radio.value);

        try {
            console.log('自动保存评分:', {
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
                this.showMessage('评分已保存', 'success');
            } else {
                this.showMessage(result.message || '评分保存失败', 'error');
            }
        } catch (error) {
            console.error('评分保存失败:', error);
            this.showMessage('网络错误，请重试', 'error');
        }
    }

    async handleComment(form) {
        const contentId = form.dataset.id;
        const contentType = form.dataset.type;
        const contentInput = form.querySelector('.comment-content');
        
        if (!contentId || !contentType || !contentInput) {
            this.showMessage('参数错误', 'error');
            return;
        }

        let content = contentInput.value.trim();

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
                contentInput.value = '';
                this.updateCommentCount(contentId, contentType, result.comment_count);
                this.loadCommentsForContent(contentId, contentType);
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
                }
            } catch (error) {
                console.error('获取用户状态失败:', error);
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
                                ${comment.rating ? `<div class="comment-rating">${this.generateStarRating(comment.rating)}</div>` : ''}
                            </div>
                            ${this.shouldShowCommentActions(comment.user.id) ? `
                            <div class="comment-actions" data-user-id="${comment.user.id}">
                                <button class="btn-edit-comment" data-comment-id="${comment.id}" title="编辑评论">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn-delete-comment" data-comment-id="${comment.id}" title="删除评论">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                            ` : ''}
                        </div>
                        <div class="comment-content">${comment.content}</div>
                        <div class="comment-edit-form" style="display: none;">
                            <textarea class="form-control edit-comment-content" placeholder="编辑评论内容...">${comment.content}</textarea>
                            <div class="edit-rating-input">
                                <label>评分:</label>
                                <div class="rating-stars">
                                    ${this.generateRatingInputs(comment.rating || 0, comment.id)}
                                </div>
                            </div>
                            <div class="edit-actions">
                                <button class="btn-save-edit" data-comment-id="${comment.id}">保存</button>
                                <button class="btn-cancel-edit" data-comment-id="${comment.id}">取消</button>
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
        // 编辑按钮事件
        container.querySelectorAll('.btn-edit-comment').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const commentId = e.target.closest('.btn-edit-comment').dataset.commentId;
                this.showEditForm(commentId);
            });
        });

        // 删除按钮事件
        container.querySelectorAll('.btn-delete-comment').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const commentId = e.target.closest('.btn-delete-comment').dataset.commentId;
                this.deleteComment(commentId);
            });
        });

        // 保存编辑按钮事件
        container.querySelectorAll('.btn-save-edit').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const commentId = e.target.closest('.btn-save-edit').dataset.commentId;
                this.saveEdit(commentId);
            });
        });

        // 取消编辑按钮事件
        container.querySelectorAll('.btn-cancel-edit').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const commentId = e.target.closest('.btn-cancel-edit').dataset.commentId;
                this.cancelEdit(commentId);
            });
        });

        // 编辑表单中的评分输入事件
        container.querySelectorAll('input[name="edit-rating"]').forEach(input => {
            input.addEventListener('change', (e) => {
                // 评分选择时不需要自动保存，只在保存编辑时一起提交
                console.log('编辑表单评分选择:', e.target.value);
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

    generateRatingInputs(currentRating = 0, commentId = '') {
        let html = '';
        for (let i = 1; i <= 5; i++) {
            const checked = i === currentRating ? 'checked' : '';
            const uniqueId = `edit-rating-${commentId}-${i}`;
            html += `
                <input type="radio" id="${uniqueId}" name="edit-rating" value="${i}" ${checked}>
                <label for="${uniqueId}">
                    <i class="fas fa-star"></i>
                </label>
            `;
        }
        return html;
    }

    showEditForm(commentId) {
        const commentItem = document.querySelector(`[data-comment-id="${commentId}"]`);
        if (!commentItem) return;

        const contentDiv = commentItem.querySelector('.comment-content');
        const editForm = commentItem.querySelector('.comment-edit-form');
        const actions = commentItem.querySelector('.comment-actions');

        // 隐藏原内容和操作按钮
        contentDiv.style.display = 'none';
        actions.style.display = 'none';
        
        // 显示编辑表单
        editForm.style.display = 'block';
    }

    cancelEdit(commentId) {
        const commentItem = document.querySelector(`[data-comment-id="${commentId}"]`);
        if (!commentItem) return;

        const contentDiv = commentItem.querySelector('.comment-content');
        const editForm = commentItem.querySelector('.comment-edit-form');
        const actions = commentItem.querySelector('.comment-actions');

        // 显示原内容和操作按钮
        contentDiv.style.display = 'block';
        actions.style.display = 'flex';
        
        // 隐藏编辑表单
        editForm.style.display = 'none';
    }

    async saveEdit(commentId) {
        const commentItem = document.querySelector(`[data-comment-id="${commentId}"]`);
        if (!commentItem) return;

        const contentTextarea = commentItem.querySelector('.edit-comment-content');
        const ratingInputs = commentItem.querySelectorAll('input[name="edit-rating"]');
        
        const newContent = contentTextarea.value.trim();
        let newRating = null;
        
        console.log('保存编辑 - 查找评分输入:', ratingInputs.length);
        for (const input of ratingInputs) {
            console.log('评分输入:', input.value, '选中状态:', input.checked);
            if (input.checked) {
                newRating = parseInt(input.value);
                break;
            }
        }

        console.log('保存编辑 - 新内容:', newContent, '新评分:', newRating);

        if (!newContent) {
            this.showMessage('评论内容不能为空', 'error');
            return;
        }

        try {
            // 构建请求数据，只有当评分存在时才包含rating字段
            const requestData = {
                content: newContent
            };
            
            // 只有当用户选择了评分时才添加rating字段
            if (newRating !== null) {
                requestData.rating = newRating;
            }

            console.log('保存编辑 - 请求数据:', requestData);

            const response = await fetch(`/api/comment/${commentId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            if (response.status === 401) {
                this.showMessage('请先登录', 'error');
                return;
            }

            const result = await response.json();
            console.log('保存编辑 - 响应结果:', result);
            
            if (result.success) {
                this.showMessage('评论更新成功', 'success');
                
                // 更新显示内容
                const contentDiv = commentItem.querySelector('.comment-content');
                contentDiv.textContent = newContent;
                
                // 更新评分显示
                const ratingDiv = commentItem.querySelector('.comment-rating');
                console.log('保存编辑 - 更新评分显示:', newRating, '现有评分div:', ratingDiv);
                
                if (newRating !== null) {
                    // 用户选择了评分，更新或创建评分显示
                    if (ratingDiv) {
                        ratingDiv.innerHTML = this.generateStarRating(newRating);
                        console.log('保存编辑 - 更新现有评分div');
                    } else {
                        const commentInfo = commentItem.querySelector('.comment-info');
                        const newRatingDiv = document.createElement('div');
                        newRatingDiv.className = 'comment-rating';
                        newRatingDiv.innerHTML = this.generateStarRating(newRating);
                        commentInfo.appendChild(newRatingDiv);
                        console.log('保存编辑 - 创建新评分div');
                    }
                } else {
                    // 用户没有选择评分，保持原有评分显示不变
                    console.log('保存编辑 - 保持原有评分显示');
                }
                
                // 更新平均评分
                const interactionSection = commentItem.closest('[data-content-id]');
                if (interactionSection) {
                    const contentId = interactionSection.dataset.contentId;
                    const contentType = interactionSection.dataset.contentType;
                    console.log('保存编辑 - 更新平均评分:', contentId, contentType, result.average_rating);
                    this.updateRating(contentId, contentType, result.average_rating);
                }
                
                // 退出编辑模式
                this.cancelEdit(commentId);
            } else {
                this.showMessage(result.message || '评论更新失败', 'error');
            }
        } catch (error) {
            console.error('评论更新失败:', error);
            this.showMessage('网络错误，请重试', 'error');
        }
    }

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

        const ratingContainer = label.closest('.rating-input') || label.closest('.edit-rating-input .rating-stars');
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

    showMessage(message, type = 'info') {
        // 创建消息提示
        const messageDiv = document.createElement('div');
        messageDiv.className = `message-toast ${type}`;
        messageDiv.textContent = message;
        
        // 添加到页面
        document.body.appendChild(messageDiv);
        
        // 触发显示动画
        setTimeout(() => {
            messageDiv.classList.add('show');
        }, 100);
        
        // 3秒后自动消失
        setTimeout(() => {
            messageDiv.classList.remove('show');
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.remove();
                }
            }, 400); // 等待动画完成
        }, 3000);
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
