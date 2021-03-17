import { mount, shallowMount } from '@vue/test-utils'

import PermissionsTableComponent from '../../src/components/permissions/PermissionsTableComponent'


const permission_data = require('./permissiondata.json')
const role_data = ["owners", "governors", "members", "friends"]


const factory = (values = {}) => {
    return shallowMount(PermissionsTableComponent, {
        propsData: {
            ...values
        }
    })
}


// haven't figured out how to mock vuex here, so can't check rendering, but can test the individual
// restructured_permsisions method where most of the logic is


describe('PermissionsTableComponent.vue', () => {
    it('restructures permissions', () => {

        const wrapper = factory({permissions: permission_data})
        expect(wrapper.props().permissions).toBe(permission_data)
        const restructured_permsisions = wrapper.vm.get_restructured_permissions(permission_data, role_data)
        expect(restructured_permsisions.length).toBe(4)

        // check perm #3
        expect(restructured_permsisions[2]["change_name"]).toBe("add members to community")
        expect(restructured_permsisions[2]["owners"]["has_perm"]).toBe(false)
        expect(restructured_permsisions[2]["governors"]["has_perm"]).toBe(true)
        expect(restructured_permsisions[2]["members"]["has_perm"]).toBe(false)
        expect(restructured_permsisions[2]["friends"]["has_perm"]).toBe(false)
        expect(restructured_permsisions[2]["anyone"]["has_perm"]).toBe(true)
        expect(restructured_permsisions[2]["you"]["has_perm"]).toBe(true)
        expect(restructured_permsisions[2]["anyone"]["more_info"]).toBe(
            "those with role governors needs to approve this action, without those with role governors rejecting. OR those with role friends needs to approve this action")

        // check perm #4
        expect(restructured_permsisions[3]["change_name"]).toBe("add post")
        expect(restructured_permsisions[3]["you"]["has_perm"]).toBe(false)

    })
    it('gets permission with least conditions', () => {
        const wrapper = factory({permissions: permission_data})
        var permA = {has_perm: false}
        var permB = {has_perm: true }
        var permC = {has_perm: true, more_info: "permC"}
        expect(wrapper.vm.update_perm(permA, true, "permD")).toEqual({has_perm: true, more_info: "permD"})
        expect(wrapper.vm.update_perm(permB, true, "permD")).toEqual({has_perm: true, more_info: null})
        expect(wrapper.vm.update_perm(permC, true, "permD")).toEqual({has_perm: true, more_info: "permC OR permD"})
        expect(wrapper.vm.update_perm(permC, true)).toEqual({has_perm: true, more_info: null})
    })
  })
