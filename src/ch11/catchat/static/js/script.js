$(document).ready(function () {
    // var socket = io.connect();
    var popupLoading = '<i class="notched circle loading icon green"></i> Loading...';
    var message_count = 0;
    var ENTER_KEY = 13;

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });

    function scrollToBottom() {
        var $messages = $('.messages');
        $messages.scrollTop($messages[0].scrollHeight);
    }

    // scroll监听函数
    var page = 1;
    function load_messages() {
        var $messages = $('.messages');
        var position = $messages.scrollTop();
        if (position === 0 && socket.nsp !== '/anonymous') {
            // 叠加页数值
            page++;
            // 激活加载滚动条
            $('.ui.loader').toggleClass('active');
            $.ajax({
                url: messages_url,
                type: 'GET',
                data: {page: page},
                success: function (data) {
                    var before_height = $messages[0].scrollHeight;
                    // 插入消息
                    $(data).prependTo(".messages").hide().fadeIn(800);
                    var after_height = $messages[0].scrollHeight;
                    // 渲染时间日期
                    flask_moment_render_all();
                    $messages.scrollTop(after_height - before_height);
                    // 关闭滚动条
                    $('.ui.loader').toggleClass('active');
                    // 激活Sematic-UI的JS组件
                    activateSemantics();
                },
                error: function () {
                    alert('No more messages.');
                    $('.ui.loader').toggleClass('active');
                }
            });
        }
    }

    $('.messages').scroll(load_messages);

    socket.on('user count', function (data) {
        $('#user-count').html(data.count);
    });

    // 在客户端创建新消息事件处理函数
    socket.on('new message', function (data) {
        // 在标签页标题中显示消息数量
        message_count++;
        if (!document.hasFocus()) {
            document.title = '(' + message_count + ') ' + 'CatChat';
        }
        if (data.user_id !== current_user_id) {
            messageNotify(data);
        }
        // 插入新消息到页面
        $('.messages').append(data.message_html);
        // 渲染消息中的时间戳
        flask_moment_render_all();
        // 进度条滚动到底部
        scrollToBottom();
        // 激活Senmatic-ui组件
        activateSemantics();
    });

    // 发送新消息
    function new_message(e) {
        var $textarea = $('#message-textarea');
        // 获取消息正文
        var message_body = $textarea.val().trim();
        if (e.which === ENTER_KEY && !e.shiftKey && message_body) {
            // 阻止默认行为，即换行
            e.preventDefault();
            // 发送事件，传入消息正文
            socket.emit('new message', message_body);
            // 清空输入框
            $textarea.val('')
        }
    }

    // submit message
    $('#message-textarea').on('keydown', new_message.bind(this));

    // submit snippet
    $('#snippet-button').on('click', function () {
        var $snippet_textarea = $('#snippet-textarea');
        var message = $snippet_textarea.val();
        if (message.trim() !== '') {
            socket.emit('new message', message);
            $snippet_textarea.val('')
        }
    });

    // open message modal on mobile
    $("#message-textarea").focus(function () {
        if (screen.width < 600) {
            $('#mobile-new-message-modal').modal('show');
            $('#mobile-message-textarea').focus()
        }
    });

    $('#send-button').on('click', function () {
        var $mobile_textarea = $('#mobile-message-textarea');
        var message = $mobile_textarea.val();
        if (message.trim() !== '') {
            socket.emit('new message', message);
            $mobile_textarea.val('')
        }
    });

    // quote message
    $('.messages').on('click', '.quote-button', function () {
        var $textarea = $('#message-textarea');
        var message = $(this).parent().parent().parent().find('.message-body').text();
        $textarea.val('> ' + message + '\n\n');
        $textarea.val($textarea.val()).focus()
    });

    // 发送新消息提醒
    function messageNotify(data) {
        if (Notification.permission !== "granted")
            Notification.requestPermission();
        else {
            var notification = new Notification("Message from " + data.nickname, {
                icon: data.gravatar,
                body: data.message_body.replace(/(<([^>]+)>)/ig, "")
            });

            notification.onclick = function () {
                window.open(root_url);
            };
            setTimeout(function () {
                notification.close()
            }, 4000);
        }
    }

    function activateSemantics() {
        $('.ui.dropdown').dropdown();
        $('.ui.checkbox').checkbox();

        $('.message .close').on('click', function () {
            $(this).closest('.message').transition('fade');
        });

        $('#toggle-sidebar').on('click', function () {
            $('.menu.sidebar').sidebar('setting', 'transition', 'overlay').sidebar('toggle');
        });

        $('#show-help-modal').on('click', function () {
            $('.ui.modal.help').modal({blurring: true}).modal('show');
        });

        $('#show-snippet-modal').on('click', function () {
            $('.ui.modal.snippet').modal({blurring: true}).modal('show');
        });

        $('.pop-card').popup({
            inline: true,
            on: 'hover',
            hoverable: true,
            html: popupLoading,
            delay: {
                show: 200,
                hide: 200
            },
            onShow: function () {
                var popup = this;
                popup.html(popupLoading);
                $.get({
                    url: $(popup).prev().data('href')
                }).done(function (data) {
                    popup.html(data);
                }).fail(function () {
                    popup.html('Failed to load profile.');
                });
            }
        });
    }

    function init() {
        // 请求开启桌面通知
        document.addEventListener('DOMContentLoaded', function () {
            if (!Notification) {
                alert('Desktop notifications not available in your browser.');
                return;
            }

            if (Notification.permission !== "granted")
                Notification.requestPermission();
        });
        // 还原标题并清零消息计数
        $(window).focus(function () {
            message_count = 0;
            document.title = 'CatChat';
        });

        activateSemantics();
        scrollToBottom();
    }

    // delete message
    $('.messages').on('click', '.delete-button', function () {
        var $this = $(this);
        $.ajax({
            type: 'DELETE',
            url: $this.data('href'),
            success: function () {
                $this.parent().parent().parent().remove();
            },
            error: function () {
                alert('Oops, something was wrong!')
            }
        });
    });

    // delete user
    $(document).on('click', '.delete-user-button', function () {
        var $this = $(this);
        $.ajax({
            type: 'DELETE',
            url: $this.data('href'),
            success: function () {
                alert('Success, this user is gone!')
            },
            error: function () {
                alert('Oops, something was wrong!')
            }
        });
    });

    init();

});
