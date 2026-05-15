sudo mkdir -p /data/TinyWiki

sudo mv tinywiki-src.tar.gz /data/TinyWiki/
sudo mv tinywiki-all-images.tar /data/TinyWiki/

cd /data/TinyWiki
sudo chown -R $(id -u):$(id -g) /data -R

tar zxvf tinywiki-src.tar.gz

sudo docker compose up -d

