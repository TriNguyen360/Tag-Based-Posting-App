"use strict";

let app = {};

// Vue app data and methods
app.data = function() {
    return {
        posts: [],             // Array to store posts
        tags: [],              // Array to store tags with their active state
        new_post_content: "",  // Content of the new post being created
        is_logged_in: is_logged_in  // Whether the user is logged in (set from server-side)
    };
};

// Methods for handling posts and tags
app.methods = {
    load_data: async function () {
        try {
            let response = await axios.get(get_posts_url);
            this.posts = response.data.posts;
            // Sort posts in reverse chronological order (newest first)
            this.posts.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
            this.updateTags(); 
        } catch (error) {
            console.error("Error loading posts:", error);
        }
    },

    // Create a new post
    createPost: async function () {
        if (!this.new_post_content.trim()) {
            // Do not create empty posts
            return;
        }
        try {
            let response = await axios.post(create_post_url, { content: this.new_post_content });
            if (response.data.post) {
                let post = response.data.post;
                this.posts.unshift(post); // Add the new post to the top of the list
                this.new_post_content = ""; // Clear the input field
                this.updateTags(); // Update tags based on the new post
            }
        } catch (error) {
            console.error("Error creating post:", error);
        }
    },

    // Delete a post
    deletePost: async function (post_id) {
        try {
            let response = await axios.post(delete_post_url, { id: post_id });
            if (response.data.success) {
                // Remove the deleted post from the posts array
                this.posts = this.posts.filter(post => post.id !== post_id);
                this.updateTags(); 
            } else {
                console.error("Failed to delete post");
            }
        } catch (error) {
            console.error("Error deleting post:", error);
        }
    },

    // Toggle a tag's active state (for filtering posts)
    toggleTag: function (tag_name) {
        let tag = this.tags.find(t => t.name === tag_name);
        if (tag) {
            tag.active = !tag.active; 
        }
    },

    // Update the tags list based on current posts
    updateTags: function () {
        let tagSet = new Set();
        this.posts.forEach(post => {
            post.tags.forEach(tag => {
                tagSet.add(tag);
            });
        });
        // Preserve the active state of existing tags
        let existingTags = {};
        this.tags.forEach(tag => {
            existingTags[tag.name] = tag.active;
        });
        // Rebuild the tags array with updated data
        this.tags = Array.from(tagSet).map(tagName => {
            return {
                name: tagName,
                active: existingTags[tagName] || false
            };
        });
    }
};

// Computed properties for the Vue app
app.computed = {
    // Filter posts based on active tags
    filteredPosts: function() {
        if (this.tags.every(tag => !tag.active)) {
            // If all tags are inactive, display all posts
            return this.posts;
        } else {
            // Display posts with at least one active tag
            let activeTags = this.tags.filter(tag => tag.active).map(tag => tag.name);
            return this.posts.filter(post => {
                return post.tags.some(tag => activeTags.includes(tag));
            });
        }
    }
};

// Initialize Vue app
app.vue = Vue.createApp({
    data: app.data,
    methods: app.methods,
    computed: app.computed,
    created() {
        this.load_data(); // Load posts when the app is created
    }
}).mount("#app");
