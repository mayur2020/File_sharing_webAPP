$('.btn-share-file').on('click',function(){
    $('#shareModal').modal()
    console.log("modal has shown...!")

    const field="xyz"
    const filenameslug = "xyz.jpg"
    const permalink = "http://localhost:1000" + '/downlaod/' + field + '/' + filenameslug +

    $('#shareModal .share-link').html(permalink)


});