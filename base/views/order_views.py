from django.shortcuts import render


# django rest framwork 
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.response import Response

from base.models import Product ,Order,OrderItem,ShippingAddress
from base.serializers import ProductSerializer,OrderSerializer

from rest_framework import status
from datetime import datetime

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addOrderItems(request):
    user = request.user #json data sent here
    data = request.data
    
    orderItems = data['orderItems']

    if orderItems and len(orderItems)==0:
        return Response({'detail':'No Order Items'},status = status.HTTP_400_BAD_REQUEST)
    else:
        # create order 
        order = Order.objects.create(
            user = user,
            paymentMethod = data['paymentMethod'],
            taxPrice = data['taxPrice'],
            shippingPrice = data['shippingPrice'],
            totalPrice = data['totalPrice'],

        )
        # create ShippingAddress 
        shipping = ShippingAddress.objects.create(
            order = order,
            address=data['shippingAddress']['address'],
            city=data['shippingAddress']['city'],
            postalCode=data['shippingAddress']['postalCode'],
            country=data['shippingAddress']['country'],

        )
        # create orderItems and add to db and set order to orderItems relationship
        for i in orderItems:
            product = Product.objects.get(_id=i['product'])
            item = OrderItem.objects.create(
                product = product,
                order=order,
                name=product.name,
                qty=i['qty'],
                price=i['price'],
                image=product.image.url,
            )
            # Update stock (decrease by no. of orderd items) for that product
            product.countInStock-= float(item.qty)
            product.save()
        serializer = OrderSerializer(order,many=False)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMyOrders(request):
    user = request.user
    orders = user.order_set.all() #gets all of this user orders
    serilizer = OrderSerializer(orders,many=True)
    return Response(serilizer.data)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def getOrders(request):
    orders = Order.objects.all() #gets all of this user orders
    serilizer = OrderSerializer(orders,many=True)
    return Response(serilizer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrderById(request,pk):
    user = request.user 
    try:
        order = Order.objects.get(_id=pk)
        if user.is_staff or order.user==user:
            serializer = OrderSerializer(order,many=False)
            return Response(serializer.data)
        else:
            Response({'detail':'Not authorized to view this order'},
                     status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({'detail':'Order does not exist'},status=status.HTTP_400_BAD_REQUEST)
     

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateOrderToPaid(request,pk):
    order = Order.objects.get(_id=pk)

    order.isPaid = True 
    order.paidAt = datetime.now()
    order.save()
    return Response('Order was Paid')
