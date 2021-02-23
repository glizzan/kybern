var swap_aliases = function swap_aliases(alias_dict, permissions) {
    const new_dict = {}
    for (const [key, value] of Object.entries(permissions)) {
        if (key in alias_dict) {
            new_dict[alias_dict[key]] = value
        } else {
            new_dict[key] = value
        }
    }
    return new_dict
}


export { swap_aliases }
