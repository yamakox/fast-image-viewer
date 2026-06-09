import uvicorn


def main():
    uvicorn.run('fast_image_viewer.asgi:application', port=8000, log_level='info')


if __name__ == '__main__':
    main()
