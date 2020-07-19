up: enable-docker
	docker-compose up --build --remove-orphans -d

# Automatically enable docker on restart
enable-docker:
	-[ -n $(shell which systemctl 2>/dev/null) ] && sudo systemctl enable docker

logs:
	docker-compose logs -f --tail=300

log_post_rotate_nginx:
	docker-compose exec frontend /bin/bash -c "killall -USR1 nginx"

down:
	docker-compose down --remove-orphans

destroy:
	docker-compose down -v --remove-orphans

.PHONY: logs log_post_rotate down destroy
