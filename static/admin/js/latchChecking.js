setInterval(function () {
    $.ajax({
        url: "/coinbase/ajaxPoll",
        type: 'POST',
        data: {'check': true},
    
        success: function (json) {
            if (json.result) {
                location.reload();
            }
        }
    });
}, 1000);
