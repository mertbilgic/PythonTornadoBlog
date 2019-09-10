$(document).ready(function(){


    $(".click").click(function(){
        console.log("searchbtn")
        if($(".searchbar").is(":visible")){
            $(".searchbar").hide();
            $(".tag").show();
        }
        else{
            $(".searchbar").show();
            $("#search").focus();
            $(".tag").hide();
        }
    });

});