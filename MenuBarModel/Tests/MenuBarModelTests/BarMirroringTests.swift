//
//  BarMirroringTests.swift
//  Project: Thaw
//
//  Copyright (Thaw) © 2026 Toni Förster
//  Licensed under the GNU GPLv3

@testable import MenuBarModel
import Testing

@Suite("Bar mirroring")
struct BarMirroringTests {
    @Test("Owners present only on the active bar are missing")
    func subtractsOwners() {
        #expect(BarMirroring.missingOwners(active: [1, 2, 3], target: [1, 2]) == [3])
    }

    @Test("Equal bars have nothing missing")
    func equalBars() {
        #expect(BarMirroring.missingOwners(active: [7, 8], target: [8, 7]).isEmpty)
    }

    @Test("The agent placeholder PID is never reported")
    func ignoresPlaceholder() {
        #expect(BarMirroring.missingOwners(active: [0, 4], target: []) == [4])
    }

    @Test("An empty active bar misses nothing")
    func emptyActive() {
        #expect(BarMirroring.missingOwners(active: [], target: [1, 2]).isEmpty)
    }
}
