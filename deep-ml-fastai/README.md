# fast.ai lab

Place notebooks in `notebooks/` and data or reusable assets in `resources/`.
Both directories are mounted into JupyterLab at `/workspace` and persist on the host.

Start the lab from the repository root:

```bash
make fastai
```

JupyterLab is available at `http://localhost:8893` by default. Configure a different port with `FASTAI_PORT` in `.env`.
