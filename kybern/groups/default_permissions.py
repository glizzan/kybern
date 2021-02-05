from concord.utils.helpers  import Changes


DEFAULT_PERMISSIONS = {
    "forum": [
        {"change_type": Changes().Groups.AddPost,
         "roles": ["members"]},
        {"change_type": Changes().Resources.AddComment,
         "roles": ["members"]}
    ]
}
