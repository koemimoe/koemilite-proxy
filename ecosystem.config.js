module.exports = {
  apps : [
      {
        name: "mediaproxy",
        script: "pipenv run hypercorn run:app --bind 0.0.0.0:5002",
        watch: true,
      }
  ]
}