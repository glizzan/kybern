from concord.actions.utils import Changes


DEFAULT_PERMISSIONS = {
    "forum": [
        {"permission_type": Changes().Groups.AddPost,
         "permission_roles": ["members"]},
        {"permission_type": Changes().Resources.AddComment,
         "permission_roles": ["members"]}
    ]
}
