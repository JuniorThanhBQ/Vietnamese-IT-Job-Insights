module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'backend',
        'frontend',
        'database',
        'crawler',
        'feature',
        'enhancement',
        'bug',
        'hotfix',
        'docker',
        'cicd',
        'documentation',
        'refactor',
        'security',
        'task',
        'release',
        'tag'
      ],
    ],
  },
};
