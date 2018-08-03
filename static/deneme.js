    $(document).ready(() => {
        $('#reg').on('click', () => {
    $.ajax({
        type:'POST',
        url:'/register',
        data:{'user': $('#UserName').val(),'pass': $('#pass').val()}
    }).done(function(data){
    if('url' in data){
        window.location=data['url']
    }else {
            $('.error').html(data['message']);
        }
        
    

    
    })
    });
    });