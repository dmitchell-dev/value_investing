from io import BytesIO
import base64
from django.contrib.auth.models import User


def get_salesman_from_id(val):
    salesman = User.objects.get(id=val)
    return salesman


def get_image(plt):
    # create a bytes buffer for the image to save
    buffer = BytesIO()
    # create the plot with the use of BytesIO object as its 'file'
    plt.savefig(buffer, format="png")
    # set the cursor the begining of the stream
    buffer.seek(0)
    # retreive the entire content of the 'file'
    image_png = buffer.getvalue()

    graph = base64.b64encode(image_png)
    graph = graph.decode("utf-8")

    # free the memory of the buffer
    buffer.close()

    return graph
