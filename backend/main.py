import uvicorn
import env


def main():
    uvicorn.run(
        'fast_image_viewer.asgi:application',
        host=env.HOST,
        port=env.PORT,
        log_level='info',
        reload=env.DEBUG,
        workers=env.WORKERS,
    )


if __name__ == '__main__':
    main()
