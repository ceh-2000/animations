import 'package:flame/components.dart';
import 'package:flame/effects.dart';
import 'package:flame/game.dart';
import 'package:flame/events.dart' as flame_events;
import 'package:flame/geometry.dart';
import 'package:flutter/widgets.dart';
import 'package:gen_animations/flower.dart';
import 'dart:html' as html; // Web only

void main() {
  runApp(GameWidget(game: AnimationRecorderGame()));
}

enum FlowerAnimation {
  FastRotate('Fast Rotate'),
  SlowRotate('Slow Rotate'),
  SwingEffect('Swing Effect'),
  SlowRotateAnti('Slow Rotate Anti-clockwise');


  final String label; // store stringified name
  const FlowerAnimation(this.label);
}

class AnimationRecorderGame extends FlameGame {
  FlowerAnimation whichAnimation = FlowerAnimation.SlowRotateAnti;
  late Flower flower;
  late TextComponent debugLog;
  late MouseTracker mouseTracker;
  late Timer loggingTimer;
  final List<String> logLines = [];

  @override
  Future<void> onLoad() async {
    debugLog = TextComponent(text: 'Hello, Flame', position: Vector2.all(16.0));

    mouseTracker = MouseTracker(debugLog);

    flower = Flower(
      size: 60,
      position: canvasSize / 4,
      onTap: (flower) {
        switch (whichAnimation) {
          case FlowerAnimation.FastRotate:
            flower.add(
              RotateAroundEffect(
                2 * tau,
                center: canvasSize / 2,
                EffectController(duration: 3),
                onComplete: () {
                  completeAnimation();
                },
              ),
            );
            break;
          case FlowerAnimation.SlowRotate:
            flower.add(
              RotateAroundEffect(
                2 * tau,
                center: canvasSize / 2,
                EffectController(duration: 6),
                onComplete: () {
                  completeAnimation();
                },
              ),
            );
            break;
          case FlowerAnimation.SwingEffect:
            flower.add(
              RotateAroundEffect(
                2.0, // radians to swing (adjust for "half moon" angle)
                center: canvasSize / 2,
                EffectController(
                  duration: 2.0,
                  reverseDuration: 2.0, // swing back
                  repeatCount: 2, // number of back-and-forth cycles
                  alternate: true, // automatically reverses direction
                ),
                onComplete: () {
                  completeAnimation();
                },
              ),
            );
            break;
          case FlowerAnimation.SlowRotateAnti:
            flower.add(
              RotateAroundEffect(
                - 2 * tau, // radians to swing (adjust for "half moon" angle)
                center: canvasSize / 2,
                EffectController(
                  duration: 6.0,
                ),
                onComplete: () {
                  completeAnimation();
                },
              ),
            );
            break;
        }

        // Start logging
        mouseTracker.isActive = true;
        logLines.clear();
        logLines.add('timestamp, mouseX, mouseY, flowerX, flowerY');
      },
    );

    add(mouseTracker);
    add(debugLog);
    add(flower);
  }

  @override
  void update(double dt) {
    super.update(dt);

    // Log every 0.01 seconds while active
    if (mouseTracker.isActive) {
      mouseTracker.accumulatedTime += dt;
      if (mouseTracker.accumulatedTime >= 0.01) {
        mouseTracker.accumulatedTime = 0;
        final mousePos = mouseTracker.lastPosition;
        final flowerPos = flower.position;
        logLines.add(
          '${DateTime.now().toIso8601String()}, '
          '${mousePos.x.toStringAsFixed(2)}, ${mousePos.y.toStringAsFixed(2)}, '
          '${flowerPos.x.toStringAsFixed(2)}, ${flowerPos.y.toStringAsFixed(2)}',
        );
      }
    }
  }

  void completeAnimation() {
    mouseTracker.isActive = false;
    downloadLog();
  }

  void downloadLog() {
    final blob = html.Blob([logLines.join('\n')], 'text/plain');
    final url = html.Url.createObjectUrlFromBlob(blob);
    final anchor = html.AnchorElement(href: url)
      ..setAttribute('download', 'rotate_around_effect_${whichAnimation}_${DateTime.now().toIso8601String()}.txt')
      ..click();
    html.Url.revokeObjectUrl(url);
  }
}

class MouseTracker extends PositionComponent
    with flame_events.PointerMoveCallbacks, HasGameRef<AnimationRecorderGame> {
  final TextComponent debugLog;
  bool isActive = false;
  Vector2 lastPosition = Vector2.zero();
  double accumulatedTime = 0;

  MouseTracker(this.debugLog) : super(size: Vector2(200, 200));

  @override
  Future<void>? onLoad() async {
    // Fill the whole canvas
    size = gameRef.size;
    position = Vector2.zero();
    return super.onLoad();
  }

  @override
  void render(Canvas canvas) {
    super.render(canvas);

    // Fill rectangle with red
    final paint = Paint()..color = const Color.fromARGB(255, 14, 0, 72);
    canvas.drawRect(size.toRect(), paint);
  }

  @override
  void onPointerMove(flame_events.PointerMoveEvent event) {
    lastPosition = event.localPosition.clone();
    if (isActive) {
      debugLog.text =
          'Cursor: (${event.localPosition.x.toStringAsFixed(2)}, ${event.localPosition.y.toStringAsFixed(2)})';
    }
  }
}
