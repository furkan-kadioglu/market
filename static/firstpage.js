$(document).ready(() => {
    
    
    $('#reg').on('click', () => {
        $.ajax({
            type:'GET',
            url:'/register',
       }).done(function(){window.location='/register'})
       
        
    });

    $('#log').on('click', () => {
        $.ajax({
            type:'GET',
            url:'/login',
       }).done(function(){window.location='/login'})
    });




});