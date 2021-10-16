function show_comments_form(parent_comment_id, button)
{
    const button_hidden = "button-hidden"
    let found_buttons = $(".button-hidden");
    if (found_buttons.length){
        found_buttons[0].classList.remove(button_hidden);
        found_buttons[0].style.display = "block";
    }
    if (parent_comment_id == 'write_comment')
    {
        $("#id_parent_comment").val('')
    }
    else
    {
        $("#id_parent_comment").val(parent_comment_id);
    }
    $("#comment_form").insertAfter("#comment-id-" + parent_comment_id);
    button.style.display = "none";
    button.classList.add(button_hidden)
}