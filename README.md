# Introduction
A simple blog based on `python3.5` and the `flask` python web framework.

### Demo
You can try it [here](https://mayatsa-flask-blog.herokuapp.com/)

### Functionality
- WYSIWYG Markdown editor based on [SimpleMDE Markdown Editor](https://simplemde.com/)
- Post management including adding, editing, deleting and image uploading
- Tag management including adding, editing and deleting(`reserved for admin`)
- User management including activating or deactivating account, changing password and grant or revoking admin rights
- Authentication including registration and logging in
- Pagination display
- Most recent posts display
- Monthly archive
- Display of tag posts
- Display of user/author posts
- API calls to return JSON

   `/api` or `/api/posts` to display the ten most recent posts
   `/api/post/<int:post_id>` to display post with `post_id`
   `/api/author/<username>` to display the ten most recent posts of author with provided `username`