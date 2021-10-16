function show_comments_form_with_text(parent_comment_id, button)
{
    if (comment_id)
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