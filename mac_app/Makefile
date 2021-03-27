.PHONY: dmg app
.DEFAULT_GOAL := help

CONDA_ROOT = /Users/psaxe/opt/anaconda3

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT


help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

app: ## Create the Mac App
	rm -fr build dist 'SEAMM Dashboard.app'
	python setup.py py2app --alias --dist-dir .
	cp -r $(CONDA_ROOT)/envs/seamm-dashboard 'SEAMM Dashboard.app/Contents/conda-env'
	sed -i '' 's|^_path_inject|#_path_inject|g' 'SEAMM Dashboard.app/Contents/Resources/__boot__.py'
	rm 'SEAMM Dashboard.app/Contents/MacOS/python'
	cd 'SEAMM Dashboard.app/Contents/MacOS' && ln -s ../conda-env/bin/python
	rm -rf 'SEAMM Dashboard.app/Contents/Resources/lib'
	cd 'SEAMM Dashboard.app/Contents/Resources' && ln -s ../conda-env/lib
	cd 'SEAMM Dashboard.app/Contents/Resources' && ln -s ../conda-env/conda-meta
	sed -i '' "s|$(CONDA_ROOT)/envs/seamm-dev|@executable_path/../conda-env|" 'SEAMM Dashboard.app/Contents/Info.plist'

dmg: ## Create a Mac disk-image (dmg)
	rm -f 'SEAMM Dashboard.dmg'
	/Users/psaxe/tmp/create-dmg/create-dmg \
		--volname "SEAMM Dashboard Installer" \
		--volicon icons.icns \
		--background background.jpg \
	        --window-pos 400 300 --window-size 600 332 \
		--icon-size 100 \
		--icon "SEAMM Dashboard.app" 150 190 \
		--hide-extension "SEAMM Dashboard.app" \
		--app-drop-link 150 40 \
		"SEAMM Dashboard.dmg" \
		"SEAMM Dashboard.app"/

