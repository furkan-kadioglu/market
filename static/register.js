$(document).ready(() => {
    $('#reg').on('click', () => {

        if($('#UserName').val() == '' || $('#pass').val() == '' ){
            error_message = "Please enter Username and Password correctly!";
            $('.error').html(error_message);
        }else {

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
        }

    });



    
});