# Ad Sites Crawler
This is a site crawler written based on crawling the iranian ad sites. For now, it only supports [Divar](https://divar.ir). 

## Run
- Install [docker](https://docs.docker.com/get-docker/) and [docker-compose](https://docs.docker.com/compose/install/).
- Run `sysctl vm.overcommit_memory=1` or set `vm.overcommit_memory=1` in `/etc/sysctl.conf` on your host and reboot your system.
- Copy `.env.sample` file to `.env` and change the values as you want.
- Run `docker-compose up --build`.

### Note
- Every time crawler find a new/changed ad, it prints the link of the ad to the console.
- You can set a [IFTTT](https://ifttt.com/create) webhook (3 value option) to get a notification when the crawler finds a new/changed ad.





