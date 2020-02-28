$(document).ready(function () {

    $(function () {
        $('[data-toggle="popover"]').popover();
    })
    // feather.replace();
    $('ul.nav > li > a[href="' + document.location.pathname + '"]').parent().addClass('active');

    $(document).on('change', ':file', function () {
        var input = $(this),
            numFiles = input.get(0).files ? input.get(0).files.length : 1,
            label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
        input.trigger('fileselect', [numFiles, label]);
    });

    // We can watch for our custom `fileselect` event like this
    $(':file').on('fileselect', function (event, numFiles, label) {
        var input = $(this).parents('.input-group').find(':text'),
            log = numFiles > 1 ? numFiles + ' files selected' : label;

        if (input.length) {
            input.val(log);
        } else {
            if (log) $('#images_upload').submit();
        }
    });
    toastr.options = {
        "closeButton": false,
        "debug": true,
        "positionClass": "toast-top-right",
        "showDuration": "300",
        "hideDuration": "1000",
        "timeOut": "5000",
        "extendedTimeOut": "1000",
        "showEasing": "swing",
        "hideEasing": "linear",
        "showMethod": "fadeIn",
        "hideMethod": "fadeOut"
    };

});

//将将链接推送给百度接口
//api 调用后台地址接口
//urls 需要推送的url，多个需要使用\n进行分割
function baidu_push_article(api,url) {
    url = window.location.protocol + '//' + window.location.host + url;
    console.log(api,url)

    $.ajax({
        type: 'POST',
        url: api,
        data: 'urls='+url,
        success: function(res){
            if(res.success > 0) {
                toastr.success('成功推送' + res.success + '个','剩余调用次数' + res.remain);
            }else {
                toastr.error('推送失败','非本站链接或链接不合法')
            }
            console.log(res)
        }
    });
}