import { shallowMount } from '@vue/test-utils'

import ForumsVuexModule from '@/store/ForumsVuexModule'


describe('ForumsVuexModule.js', () => {
    const state = {
        forums: [
            {pk: 1, name: "A Forum", description: "Look a forum"},
            {pk: 2, name: "Another Forum", description: "Look another forum"}
        ],
        posts: [
            {pk: 1, forum_pk: 2, title: "A Post", content: "Look a post", author: 12}
        ]
    }
    // test state
    it('has no posts', () => {
      expect(ForumsVuexModule.state.posts).toEqual([])
    })
    it('has no forums', () => {
        expect(ForumsVuexModule.state.forums).toEqual([])
    })
    // test getters
    it('gets forum data given forum_pk', () => {
        expect(ForumsVuexModule.getters.getForumData(state)(1)).toEqual({pk: 1, name: "A Forum", description: "Look a forum"})
    })
    it('gets post data for forum', () => {
        expect(ForumsVuexModule.getters.getPostsDataForForum(state)(2)).toEqual([{pk: 1, forum_pk: 2, title: "A Post", content: "Look a post", author: 12}])
    })
    it('gets post data for post pk', () => {
        expect(ForumsVuexModule.getters.getPostData(state)(1)).toEqual({pk: 1, forum_pk: 2, title: "A Post", content: "Look a post", author: 12})
    })

  })