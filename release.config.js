module.exports = {
	branches: ["master", {"name": "dev", "prerelease": true}],
	repositoryUrl: "https://github.com/devops-dislinkt/user-post.git",
	plugins: [
		"@semantic-release/commit-analyzer",
		"@semantic-release/release-notes-generator",
		["@semantic-release/github", {
			assets: [
				{"path": "dist/*.gz", "label": "Build"},
				{"path": "coverage.xml", "label": "Code coverage"}
			]
		}
		]
	]
}