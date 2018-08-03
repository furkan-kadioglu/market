$(document).ready(() => {

    $('.button').on('click', () => {

        if ($('#user').val()=='' || $('#pass').val()==''){
            error_message = "it is not ok!";
            $('.error').html(error_message);
 
        }else{
            $.ajax({
                type:'POST',
                url:'/login',
                data:{'user': $('#user').val(),'pass': $('#pass').val()}
           }).done(function(data){
               if(data['url'] == '/login'){
                    error_message = "it is not ok!";
                    $('.error').html(error_message);
               }else{
                window.location= data['url']
               }
               
           })
           

        }
        

    });
    
    
    /*$('body').on('keyup', e => {
        if(e.keyCode == 16){
            $.ajax({
                type:'POST',
                url:'/login',
                data:{'user': $('#user').val(),'pass': $('#pass').val()}
           }).done(function(data){
               window.location= data['url']
           })
        }
    });*/
    

});