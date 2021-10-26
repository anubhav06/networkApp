document.addEventListener('DOMContentLoaded', function() {

    document.addEventListener('click', event => {
        
        const element = event.target;

        // Get the clicked element id and check if it contains `edit-btn`
        if(element.id.indexOf('edit-btn') > -1){
            // Get the clicked element id and split the actuall id from `edit-btn`
            const id = element.id.split('edit-btn')[1]
            document.querySelector(`#post${id}`).style.display = `none`
            document.querySelector(`#editPost${id}`).style.display = 'block'
        } 


        if(element.id.indexOf('edit-form-submit') > -1){
            // Get the clicked element id and split the actuall id from `edit-form-submit`
            const id = element.id.split('edit-form-submit')[1]
            editFormSubmit(id)
            document.querySelector(`#post${id}`).style.display = `block`
            document.querySelector(`#editPost${id}`).style.display = `none`
        }
        

        if(element.id.indexOf('like-btn') > -1){

            // Get the clicked element id and split the actuall id from `like-btn`
            const id = element.id.split('like-btn')[1]

            // If its not liked
            if (element.style.backgroundColor == 'white'){
                canLike = true
                canUnlike = false
            }       
            // If its already liked
            else if (element.style.backgroundColor == 'red'){
                canUnlike = true
                canLike = false
            }

            if (canLike == true){
                like(id, canLike, canUnlike)
            }
            else if(canUnlike == true){
                unlike(id, canLike, canUnlike )
            }
        }
    })

})


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function editFormSubmit(id){

    const csrftoken = getCookie('csrftoken');

    fetch("/edit", {
        headers: { "X-CSRFToken": csrftoken },
        method: "POST",
        body: JSON.stringify({
            id : id,
            content : document.querySelector(`#edit-content${id}`).value
        })
    })
    .then(response => response.json())
    .then( post => {
        // Show the updated data
        document.querySelector(`#content${id}`).innerHTML = `${post[0].content}`
    })

    return false;
};


function like(id, canLike, canUnlike){
    
    const csrftoken = getCookie('csrftoken')

    fetch("/like", {
        headers: { "X-CSRFToken": csrftoken },
        method: "POST",
        body: JSON.stringify({
            likes : document.querySelector(`#likes${id}`).value,
            id : id
        })
    })
    .then(response => response.json)
    .then( () => {
        document.querySelector(`#like-btn${id}`).style.backgroundColor = 'Red'
        var oldLikes = document.querySelector(`#noOfLikes${id}`).innerHTML;
        oldLikes = parseInt(oldLikes)
        document.querySelector(`#noOfLikes${id}`).innerHTML = `${oldLikes + 1}`
        
        canUnlike = true
        canLike = false
    })

}

function unlike(id, canLike, canUnlike){
    
    const csrftoken = getCookie('csrftoken')

    fetch("/unlike", {
        headers: { "X-CSRFToken": csrftoken },
        method: "POST",
        body: JSON.stringify({
            likes : document.querySelector(`#likes${id}`).value,
            id : id
        })
    })
    .then(response => response.json)
    .then( () => {
        document.querySelector(`#like-btn${id}`).style.backgroundColor = 'white'
        var oldLikes = document.querySelector(`#noOfLikes${id}`).innerHTML;
        oldLikes = parseInt(oldLikes)
        document.querySelector(`#noOfLikes${id}`).innerHTML = `${oldLikes - 1}`

        canLike = true
        canUnlike = false
    })

}