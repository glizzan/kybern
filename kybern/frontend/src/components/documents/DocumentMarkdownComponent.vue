<template>

    <span>

        <b-row class="py-3">
            <b-col cols=12>
                Write your document below. You can use
                    <a href="https://www.markdownguide.org/basic-syntax/">Markdown</a> syntax for style.
            </b-col>
        </b-row>

        <b-row >
            <b-col cols=6>
                <b-form-textarea id="document_content_textarea" name="document_content_textarea"
                    v-model="current_content" rows="5" @input="update" class="w-100"></b-form-textarea>
            </b-col>
            <b-col cols=6>
                <div v-html="compiledMarkdown"></div>
            </b-col>
        </b-row>

    </span>

</template>

<script>

import Vuex from 'vuex'
import { debounce } from 'lodash'
import marked from 'marked'
import store from '../../store'


export default {

    props: ['content'],
    store,
    data: function() {
        return {
            current_content: '# hello!'
        }
    },
    created () {
        if (this.content) { this.current_content = this.content }
    },
    watch: {
        content: function(val) {
            console.log("Time to overwrite! with ", this.content)
            if (typeof this.content !== "undefined") {
                this.current_content = this.content
            }
        }
    },
    computed: {
        compiledMarkdown() {
            return marked(this.current_content, { sanitize: true });
        }
    },
    methods: {
        update: debounce(function(e) {
            this.current_content = e.target.value;
        }, 300)
    }

}

</script>