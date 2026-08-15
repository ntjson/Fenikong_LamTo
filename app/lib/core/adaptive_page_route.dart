import 'package:flutter/cupertino.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

PageRoute<T> adaptivePageRoute<T>({required WidgetBuilder builder}) =>
    defaultTargetPlatform == TargetPlatform.iOS
    ? CupertinoPageRoute<T>(builder: builder)
    : MaterialPageRoute<T>(builder: builder);
