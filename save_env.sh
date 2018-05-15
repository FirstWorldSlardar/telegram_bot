echo "activating env.."
source activate telegram_env
echo "saving env requirements in env.yaml.."
conda env export > env.yaml
echo "Done."
